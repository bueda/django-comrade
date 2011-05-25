from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from django.http import (HttpResponsePermanentRedirect, get_host, HttpResponse,
        Http404)
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from django.contrib.auth.views import redirect_to_login

import re
import itertools

try:
    # Import Piston if it's installed, but don't die if it's not here. Only a
    # limited number of Middleware require it.
    import piston.utils

    # Importing this registers translators for the MimeTypes we are using.
    import piston.emitters
except ImportError:
    pass

from comrade.http import coerce_put_post
from comrade.views.simple import direct_to_template

import commonware.log
logger = commonware.log.getLogger(__name__)


_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_SUPPORTED_TRANSFORMS = ['PUT', 'DELETE']
_FORM_RE = re.compile(r'((<form\W[^>]*\bmethod=(\'|"|))(%s)((\'|"|)\b[^>]*>))'
        % '|'.join(_SUPPORTED_TRANSFORMS), re.IGNORECASE)
_MIDDLEWARE_KEY = '_method'
SSL = 'SSL'


class HttpMethodsMiddleware(object):
    """Allows you to use methods other than GET/POST in HTML forms.

    This rewrites the responses to use POST and to store the actual method in a
    hidden form input. When processing requests it looks for the intended method
    on the from data and patches the request object.

    You need to be careful with this middleware, as Django's CSRF view
    middleware doesn't enforce a token requirement if the method is anything
    besides POST. You MUST use the MultiMethodCsrfViewMiddleware in conjunction
    with this middleware (and instead of Django's own CsrfViewMiddleware).
    """

    def __init__(self):
        if ('django.middleware.csrf.CsrfViewMiddleware' in
                settings.MIDDLEWARE_CLASSES):
            raise ImproperlyConfigured("To use CSRF protection with the "
                    "HttpMethodsMiddleware, you muse use the "
                    "MultiMethodCsrfViewMiddleware instead of Django's "
                    "CsrfViewMiddleware.")

    def process_request(self, request):
        if request.POST and request.POST.has_key(_MIDDLEWARE_KEY):
            if request.POST[_MIDDLEWARE_KEY].upper() in _SUPPORTED_TRANSFORMS:
                request.method = request.POST[_MIDDLEWARE_KEY].upper()

        coerce_put_post(request)
        return None

    def process_response(self, request, response):
        if response['Content-Type'].split(';')[0] in _HTML_TYPES:
            # ensure we don't add the 'id' attribute twice (HTML validity)
            idattributes = itertools.chain(("id='" + _MIDDLEWARE_KEY + "'",),
                                            itertools.repeat(''))
            def add_transform_field(match):
                """Returns the matched <form> tag with a modified method and
                the added <input> element"""
                return match.group(2) + "POST" + match.group(5) + \
                "<div style='display:none;'>" + \
                "<input type='hidden' " + idattributes.next() + \
                " name='" + _MIDDLEWARE_KEY + "' value='" + \
                match.group(4).upper() + "' /></div>"

            # Modify any POST forms
            response.content = _FORM_RE.sub(add_transform_field,
                    response.content)
        return response


class MultiMethodCsrfViewMiddleware(CsrfViewMiddleware):
    """To be used in conjunction with HttpMethodsMiddleware, this changes the
    request's HTTP method back to POST if it was modified to PUT/DELETE so CSRF
    token checking will still occur.

    Seriously, don't forget to use this! The Django ticket #15258 proposes
    expanding the CSRF protection to PUT and DELETE, but until then this is
    neccessary.
    """

    def process_view(self, request, callback, callback_args, callback_kwargs):
        original_method = request.method
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            request.method = 'POST'
        response = super(MultiMethodCsrfViewMiddleware, self).process_view(
                request, callback, callback_args, callback_kwargs)
        request.method = original_method
        return response


class ForwardedSSLMiddleware(object):
    def process_request(self, request):
        request.is_secure = lambda: request.META.get(
                'HTTP_X_FORWARDED_PROTO') == 'https'


class SslRedirectMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        secure = view_kwargs.pop(SSL, True)
        if settings.SSL_ENABLED and secure and not request.is_secure():
            return self._redirect(request, secure)

    def _redirect(self, request, secure):
        protocol = 'https' if secure else 'http'
        url = "%s://%s%s" % (protocol, get_host(request),
                request.get_full_path())
        if settings.DEBUG and request.method == 'POST':
            raise RuntimeError, \
        """Django can't perform a SSL redirect while maintaining POST data.
           Structure your views so that redirects only occur during GETs."""
        return HttpResponsePermanentRedirect(url)


class PermissionRedirectMiddleware(object):
    """Middleware that catches any PermissionDenied errors that haven't been
    caught in the view and redirects the user to the login page. This allows any helper
    method simple raise a PermissionDenied instead of needing the check if
    helper methods return an HttpResponse.

    """
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
            # TODO this likely needs to be much, much smarter
            if 'json' in request.accepted_types[0]:
                return HttpResponse(status=401)
            elif request.user.is_authenticated():
                return direct_to_template(request, "403.html",
                        {'message': str(exception)}, status=403)
            else:
                return redirect_to_login(request.path)


class POSTDataMassageMiddleware(object):
    """Middleware to take all POST data - whether JSON, form encoded fields,
    XML, etc. and store it in the `data` attribute on the request.

    Sets `request.multipart` to True if content_type is multipart.

    Requires django-piston.
    """
    def process_request(self, request):
        if request.method in ('POST', 'PUT'):
            try:
                piston.utils.translate_mime(request)
            except piston.utils.MimerDataException:
                return piston.utils.rc.BAD_REQUEST
            else:
                request.multipart = piston.utils.Mimer(request).is_multipart()
            if not hasattr(request, 'data'):
                if request.method == 'POST':
                    request.data = request.POST
                elif request.method == 'PUT':
                    request.data = request.PUT


class AcceptMiddleware(object):
    def _parse_accept_header(self, accept):
        """Parse the Accept header *accept*, returning a list with pairs of
        (media_type, q_value), ordered by q values.
        """
        result = []
        for media_range in accept.split(","):
            parts = media_range.split(";")
            media_type = parts.pop(0)
            media_params = []
            q = 1.0
            for part in parts:
                (key, value) = part.lstrip().split("=", 1)
                if key == "q":
                    q = float(value)
                else:
                    media_params.append((key, value))
            result.append((media_type, tuple(media_params), q))
        result.sort(lambda x, y: -cmp(x[2], y[2]))
        return result

    def process_request(self, request):
        accept = self._parse_accept_header(request.META.get("HTTP_ACCEPT", ""))
        request.accept = accept
        request.accepted_types = map(lambda (t, p, q): t, accept)

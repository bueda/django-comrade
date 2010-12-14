from django.conf import settings
from django.http import (HttpResponsePermanentRedirect, get_host)
from django.core.exceptions import PermissionDenied
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

from comrade.core.router import coerce_put_post

import logging
logger = logging.getLogger(__name__)


_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_SUPPORTED_TRANSFORMS = ['PUT', 'DELETE']
_FORM_RE = re.compile(r'((<form\W[^>]*\bmethod=(\'|"|))(%s)((\'|"|)\b[^>]*>))'
        % '|'.join(_SUPPORTED_TRANSFORMS), re.IGNORECASE)
_MIDDLEWARE_KEY = '_method'
SSL = 'SSL'

class HttpMethodsMiddleware(object):
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


class SslRedirectMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        secure = view_kwargs.pop(SSL, False)
        if settings.SSL_ENABLED and secure != request.is_secure():
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


class ArgumentLogMiddleware(object):
    ignored_modules = ['debug_toolbar.views',
            'django.views.static',]

    def process_view(self, request, view, args, kwargs):
        if hasattr(view, '__name__'):
            name = view.__name__
        elif hasattr(view, '__class__'):
            name = view.__class__
        else:
            name = ''
        if view.__module__ not in self.ignored_modules:
            logger.debug('Calling %s.%s' % (view.__module__, name))
            if kwargs or args:
                logger.debug('Arguments: %s' % (kwargs or (args,)))


class PermissionRedirectMiddleware(object):
    """Middleware that catches any PermissionDenied errors that haven't been
    caught in the view and redirects the user to the login page. This allows any helper
    method simple raise a PermissionDenied instead of needing the check if
    helper methods return an HttpResponse.

    This middleware will not be required as soon as this patch lands in Django:
    http://code.djangoproject.com/ticket/13850 - after that we can just define a
    customer 403 handler that redirects instead of renders.

    """
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionDenied):
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

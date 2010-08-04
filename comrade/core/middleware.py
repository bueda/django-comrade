from django.conf import settings
from django.http import (HttpResponsePermanentRedirect, get_host,
        HttpResponseRedirect)
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

from comrade.views.simple import direct_to_template

import re
import itertools

import logging
logger = logging.getLogger('comrade.cron')


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
    def process_view(self, request, view, args, kwargs):
        logger.debug('Calling %s.%s' % (view.__module__, view.__name__))
        logger.debug('Arguments: %s' % (kwargs or (args,)))


class PermissionRedirectMiddleware(object):
    """Middleware that checks that the user passes the given test,
    redirecting to the unauthorized page if it fails. The test should be a
    callable that takes the user object and returns True if the user passes.
    
    This middleware must be the last of any view middleware, as it actually
    renders the view and returns a response.
    """
    def __init__(self, test_func=None, template='401.html', args=None,
            kwargs=None):
        self.template = template
        self.test_func = test_func
        self.args = args or ()
        self.kwargs = kwargs or {}

    def process_view(self, request, view, args, kwargs):
        try:
            if self.test_func and self.test_func(request.user, *args, **kwargs):
                return view(request, *args, **kwargs)
            else:
                raise PermissionDenied
        except PermissionDenied:
            return direct_to_template(request, self.template, status=401)

from django.http import Http404

import commonware.log
logger = commonware.log.getLogger(__name__)


class ArgumentLogMiddleware(object):
    ignored_modules = ['debug_toolbar.views',
            'django.views.static',
            'django.contrib.staticfiles.views']

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


class ExceptionLoggingMiddlware(object):
    def process_exception(self, request, exception):
        if not isinstance(exception, Http404):
            logger.exception("Unhandled exception:")

from django.http import (HttpResponse, HttpResponseServerError,
        HttpResponseForbidden)
from django.template import RequestContext, loader
from django.conf import settings

import commonware.log
logger = commonware.log.getLogger(__name__)

def csrf_failure(request, reason='', template_name='403.html'):
    logger.debug("CSRF failure: %s", reason)
    t = loader.get_template(template_name)
    context = {'message': "Do you have cookies enabled? This site requires "
            "cookies to operate."}
    return HttpResponseForbidden(t.render(RequestContext(request, context)))

def status(request, **kwargs):
    logger.debug("Responding to status check")
    return HttpResponse()

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))

def maintenance_mode(request, template_name='503.html'):
    from maintenancemode.http import HttpResponseTemporaryUnavailable

    t = loader.get_template(template_name)
    return HttpResponseTemporaryUnavailable(t.render(RequestContext(request)))

def version(request, version_attribute='GIT_COMMIT', **kwargs):
    return HttpResponse(getattr(settings, version_attribute))

def direct_to_template(request, template, extra_context=None, mimetype=None,
        status=None, **kwargs):
    '''
    Duplicates behavior of django.views.generic.simple.direct_to_template
    but accepts a status argument.
    '''
    if extra_context is None:
        extra_context = {}

    dictionary = {'params': kwargs}
    for key, value in extra_context.items():
        if callable(value):
            dictionary[key] = value()
        else:
            dictionary[key] = value

    c = RequestContext(request, dictionary)
    t = loader.get_template(template)

    return HttpResponse(t.render(c), status=status,
            mimetype=mimetype)

from django.http import HttpResponse, HttpResponseServerError
from django.template import RequestContext, loader
from django.conf import settings

from maintenancemode.http import HttpResponseTemporaryUnavailable

import logging
logger = logging.getLogger('comrade.views.simple')

def status(request):
    logger.info("Responding to status check")
    return HttpResponse()

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name) 
    return HttpResponseServerError(t.render(RequestContext(request)))

def maintenance_mode(request, template_name='503.html'):
    t = loader.get_template(template_name)
    return HttpResponseTemporaryUnavailable(t.render(RequestContext(request)))

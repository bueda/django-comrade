from django.http import HttpResponse, HttpResponseServerError
from django.template import Context, loader
from django.conf import settings

import commonware.log
logger = commonware.log.getLogger('comrade.views.simple')

def status(request):
    logger.info("Responding to status check")
    return HttpResponse()

def server_error(request, template_name='500.html'):
    t = loader.get_template(template_name) 
    return HttpResponseServerError(
            t.render(Context({ 'MEDIA_URL': settings.MEDIA_URL })))

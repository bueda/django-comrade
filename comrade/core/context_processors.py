from django.conf import settings
from django.contrib.sites.models import Site
from settings import DeploymentType

def default(request):
    context = {}
    context['DEPLOYMENT'] = settings.DEPLOYMENT
    context['site'] = Site.objects.get_current()
    if settings.DEPLOYMENT != DeploymentType.PRODUCTION:
        context['GIT_COMMIT'] = settings.GIT_COMMIT
    return context

def ssl_media(request):
    if request.is_secure():
        ssl_media_url = settings.MEDIA_URL.replace('http://','https://')
    else:
        ssl_media_url = settings.MEDIA_URL
    return {'MEDIA_URL': ssl_media_url}

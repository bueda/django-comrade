from django.conf import settings
from django.contrib.sites.models import Site
from settings import DeploymentType

def context_processor(request):
    context = {}
    context['DEPLOYMENT'] = settings.DEPLOYMENT
    context['site'] = Site.objects.get_current()
    if settings.DEPLOYMENT != DeploymentType.PRODUCTION:
        context['GIT_COMMIT'] = settings.GIT_COMMIT
    return context

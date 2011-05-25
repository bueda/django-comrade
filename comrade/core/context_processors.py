from django.conf import settings
from django.contrib.sites.models import Site
from settings import DeploymentType


def default(request):
    context = {}
    context['DEPLOYMENT'] = settings.DEPLOYMENT
    context['current_site'] = Site.objects.get_current()
    if settings.DEPLOYMENT != DeploymentType.PRODUCTION:
        context['GIT_COMMIT'] = settings.GIT_COMMIT
    context['site_email'] = settings.CONTACT_EMAIL
    if request.is_secure():
        context['protocol'] = 'https://'
    else:
        context['protocol'] = 'http://'
    context['current_site_url'] = (context['protocol'] +
            context['current_site'].domain)
    return context


def profile(request):
    context = {}
    if request.user.is_authenticated():
        context['profile'] = lambda: request.user.get_profile()
    return context

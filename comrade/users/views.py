from django.conf import settings
from django.contrib.auth import login as auth_login, REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm

import re

from comrade.users import multipass
from comrade.views.simple import direct_to_template

import commonware.log
logger = commonware.log.getLogger(__name__)

def _add_sso(request, use_multipass, tender_url, redirect_to):
    if use_multipass and redirect_to == tender_url:
            redirect_to += '?sso=' + multipass.multipass(request.user)
    return redirect_to

def login(request, multipass=False, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    tender_url = getattr(settings, 'TENDER_URL', None)
    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    # Heavier security check -- redirects to http://example.com should
    # not be allowed, but things like /view/?param=http://example.com
    # should be allowed. This regex checks if there is a '//' *before* a
    # question mark. Unless of course, the redirect is to the Tender
    # app.
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        if redirect_to != tender_url:
            redirect_to = settings.LOGIN_REDIRECT_URL

    if request.user.is_authenticated():
        redirect_to = _add_sso(request, multipass, tender_url, redirect_to)
        return HttpResponseRedirect(redirect_to)

    if request.method == "POST":
        form = authentication_form(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            redirect_to = _add_sso(request, multipass, tender_url, redirect_to)
            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    if multipass:
        login_url = reverse('account:multipass_login')
    else:
        login_url = reverse('account:login')

    request.session.set_test_cookie()
    return direct_to_template(request, template_name, {
        'form': form,
        'redirect_field_name': redirect_field_name,
        'redirect_to': redirect_to,
        'login_url': login_url})

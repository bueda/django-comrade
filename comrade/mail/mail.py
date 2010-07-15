from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

def direct_to_email(template, recipient_list, extra_context=None,
        from_email=None, subject_template=None):
    """
    Sends an email of type email to user.email. Text of subject and message
    rendered from the {template} and {template}_subject using specified context
    """
    extra_context = extra_context or {}
    context = Context(extra_context)
    context['site'] = Site.objects.get_current()
    if not subject_template:
        subject = render_to_string(
                '%s_subject.txt' % template, context).strip('\n')
    message = render_to_string('%s.txt' % template, context)

    return EmailMessage(subject, message, from_email, recipient_list,
            headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}).send()

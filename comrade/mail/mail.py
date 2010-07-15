from django.conf import settings
from django.core.mail import EmailMessage
from django.template import RequestContext
from django.template.loader import render_to_string

def direct_to_email(template, recipient_list, form_email=None,
        extra_context=None, subject_template=None):
    """
    Sends an email of type email to user.email. Text of subject and message
    rendered from templates/mail/{email}.txt and templates/mail/{email}_subject.txt
    usign specified context
    """
    extra_context = extra_context or {}
    context = RequestContext(extra_context)
    if not subject_template:
        subject = render_to_string('mail/%s_subject.txt' % template, context)
    body = render_to_string('mail/%s.txt' % template, context)

    return EmailMessage(subject, body, recipient_list,
            headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}).send()

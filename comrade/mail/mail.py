from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

import re

from comrade.mail.signals import email_sent

def direct_to_email(template, recipient_list, extra_context=None,
        from_email=None, subject_template=None):
    """
    Sends an email of type email to user.email. Text of subject and message
    rendered from the {template} and {template}_subject using specified context
    """
    extra_context = extra_context or {}
    context = Context(extra_context)
    context['current_site'] = Site.objects.get_current()
    if not subject_template:
        subject = render_to_string(
                '%s_subject.txt' % template, context).strip('\n')
    message = render_to_string('%s.txt' % template, context)

    email_sent.send(sender=template, recipient_list=recipient_list,
            from_address=(from_email or settings.DEFAULT_FROM_EMAIL))

    return EmailMessage(subject, message, from_email, recipient_list,
            headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}).send()

# Inspired by
# http://stackoverflow.com/questions/1372694/strip-signatures-and-replies-from-emails/2193937#2193937
EMAIL_SIGNATURES = (
        # standard
        re.compile(r'^-- \r*\n$', flags=re.MULTILINE),
        # standard missing space
        re.compile(r'^--\r*\n$', flags=re.MULTILINE),
        # ego-booster
        re.compile(r'^Sent from my', flags=re.MULTILINE),
)

def strip_signatures(body):
    for signature in EMAIL_SIGNATURES:
        split_signature = signature.split(body)
        if len(split_signature) > 1:
            return split_signature[0].strip()
    return body

EMAIL_QUOTED_MARKERS = (
        # outlook
        re.compile(r'^-----Original Message-----', flags=re.MULTILINE),
        # outlook alternative
        re.compile(r'^________________________________', flags=re.MULTILINE),
        # mail.app
        re.compile(r'^On .+wrote:\r*\n', flags=re.MULTILINE),
        # failsafe
        re.compile(r'^From: ', flags=re.MULTILINE),
        # indented
        re.compile(r'^>.*$', flags=re.MULTILINE),
)

def strip_quoted(body):
    for quoted in EMAIL_QUOTED_MARKERS:
        split_message = quoted.split(body)
        if len(split_message) > 1:
            return split_message[0].strip()
    return body

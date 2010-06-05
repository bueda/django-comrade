from django.conf import settings
from django.core.mail import EmailMessage

def send_mail(subject, message, recipient_list, from_email=None):
    """
    Easy wrapper around Django's easy wrapper of the mail interface.

    Does the same thing as send_mail, but with a couple of Bueda additions.
    """
    return EmailMessage(subject, message, from_email, recipient_list,
            headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}).send()

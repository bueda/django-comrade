from django.core import mail
import re

def delivered(pattern, to_queue=None):
    """
    Checks that a message with that pattern is delivered via the Django mail
    outbox, and then returns it.

    It does this by searching through the Django mailbox and finding anything
    that matches the pattern regex.
    """
    for message in mail.outbox:
        regp = re.compile(pattern)
        for candidate in message.to + [message.from_email,
                message.extra_headers.get('Reply-To', ''), message.body,
                message.subject]:
            if regp.search(candidate) is not None:
                return message
    return False

from comrade.mail.signals import email_sent
from comrade.mail.models import EmailEvent

email_sent.connect(EmailEvent.objects.create_from_signal)


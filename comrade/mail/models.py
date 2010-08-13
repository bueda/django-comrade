from django.db import models

from comrade.core.models import ComradeBaseModel


class EmailEventManager(models.Manager):
    def create_from_signal(self, **kwargs):
        """
        Called when an email_sent signal is sent, passed from address,
        list of recipient emails, and brief description and creates appropriate
        objects
        """
        try:
            from_address = kwargs['from_address']
            recipient_list = kwargs['recipient_list']
            description = kwargs['description']
        except KeyError, e:
            raise TypeError("EmailEvent.create_from_signal requires keyword "
                    "arg %s" % e[0])

        email_event = EmailEvent(from_address=from_address,
                description=description)
        email_event.save()
        for recipient in recipient_list:
            EmailEventRecipient(email_event=email_event,
                    to_address=recipient).save()
        return email_event

class EmailEvent(ComradeBaseModel):
    from_address = models.EmailField()
    description = models.CharField(max_length=255)
    # created from ComradeBaseModel

    @property
    def recipients(self):
        return [recipient.to_address for recipient in
                self.emaileventrecipient_set.all()]

    def __unicode__(self):
        return "EmailEvent(description: %s, created: %s)" % (
                self.description, self.created)

    objects = EmailEventManager()


class EmailEventRecipient(ComradeBaseModel):
    """
    Store the 'to' email addresses of an email sent event
    """
    email_event = models.ForeignKey(EmailEvent)
    to_address = models.EmailField()

    def __unicode__(self):
        return "Recipient(%s)" % self.to_address


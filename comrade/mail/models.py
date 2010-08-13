from django.db import models

from comrade.core.models import ComradeBaseModel

class EmailEventManager(models.Manager):
    def create_from_signal(self, sender, from_address, recipient_list,
            **kwargs):
        """
        Called when an email_sent signal is sent, passed from address,
        list of recipient emails, and brief description and creates appropriate
        objects
        """
        return self.create(recipients=",".join(recipient_list),
                from_address=from_address, description=sender)

class EmailEvent(ComradeBaseModel):
    from_address = models.EmailField(editable=False)
    description = models.CharField(max_length=255, editable=False)
    recipients = models.CharField(max_length=255, editable=False)

    def __unicode__(self):
        return "EmailEvent(description: %s, created: %s)" % (
                self.description, self.created)

    objects = EmailEventManager()

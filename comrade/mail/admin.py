from django.contrib import admin

from comrade.mail.models import EmailEvent


class EmailEventAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'recipients',)

admin.site.register(EmailEvent, EmailEventAdmin)


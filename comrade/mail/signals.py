from django.dispatch import Signal

email_sent = Signal(providing_args=["from_address", "recipient_list",
        "description"])

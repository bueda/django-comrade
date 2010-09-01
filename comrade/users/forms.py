from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LongAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=255)

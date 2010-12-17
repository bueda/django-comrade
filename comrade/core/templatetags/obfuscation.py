from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

import string

register = template.Library()

@register.filter
@stringfilter
def obfuscate_email(email):
    obfuscated = ""
    for char in email:
        try:
            output = (string.ascii_lowercase.index(char) + 97
                    if char in string.ascii_lowercase else None)
            output = (string.ascii_uppercase.index(char) + 65
                    if char in string.ascii_uppercase else output)
        except ValueError:
            output = None
        if output:
            output = "&#%s;" % output
        elif char == '@':
            output = '&#0064;'
        else:
            output = char
        obfuscated += output
    return mark_safe(obfuscated)


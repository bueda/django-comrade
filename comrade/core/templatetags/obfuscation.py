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

class PartialNode(template.Node):
    def __init__(self, partial, params):
        super(PartialNode, self).__init__()
        self.partial = partial
        self.params = params

    def render(self, context):
        context_params = {}
        for k, v in self.params.items():
            try:
                context_params[k] = eval(v)
            except:
                context_params[k] = template.Variable(v).resolve(context)
        t = template.loader.get_template(self.partial)
        return t.render(template.Context(context_params))

@register.tag
def render_partial(parser, token):
    parts = token.split_contents()
    params = {}
    try:
        tag_name, partial = parts[:2]
        if partial.startswith('"'):
            partial = partial[1:-1]
        for p in parts[2:]:
            k, v = p.split(':')
            params[k] = v
    except ValueError:
        raise template.TemplateSyntaxError, (
                '%r tag requires at least a single argument and no '
                'spaces in name:value list' % parts[0])

    return PartialNode(partial, params)

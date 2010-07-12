from django import template

register = template.Library()

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

from django.views.generic.base import TemplateResponseMixin

class PartialMixin(object):
    def _render_partial(self):
        return (self.request.is_ajax() and
                ('text/html' in self.request.accepted_types
                or self.request.GET.get('format', '') == 'partial'))


class PartialTemplateResponseMixin(TemplateResponseMixin, PartialMixin):
    """Return a Rails-style parital HTML fragment if ?format=partial.

    This mixin requires that you specify an additional Django template beyond
    the one for normal requests, this one a smaller fragment or partial. The
    mixin is useful if you have a complicated bit of HTML that you are loading
    via an AJAX call, but don't want to construct in JavaScript.
    """
    partial_template_name = None

    def get_template_names(self):
        if self._render_partial():
            if self.partial_template_name is None:
                return []
            else:
                return [self.partial_template_name]
        return super(PartialTemplateResponseMixin, self).get_template_names()

from django.views.generic.list import (BaseListView,
        MultipleObjectTemplateResponseMixin)

from partial import PartialTemplateResponseMixin
from detail import PKSafeSingleObjectMixin
from content import ContentNegotiationMixin

class HybridListView(PKSafeSingleObjectMixin, ContentNegotiationMixin,
        MultipleObjectTemplateResponseMixin, PartialTemplateResponseMixin,
        BaseListView):
    """Return an object list view, either HTML, JSON or XML (depending on the
    ACCEPT HTTP header or ?format=x query parameter.
    """
    api_context_exclude_keys = set(['paginator', 'page_obj', 'is_paginated',
            'object_list',])

    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = MultipleObjectTemplateResponseMixin.render_to_response(
                    self, context, **kwargs)
        return response

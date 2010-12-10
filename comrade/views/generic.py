from django import http
from django.core import serializers
from django.views.generic.list import (BaseListView,
        MultipleObjectTemplateResponseMixin)
from django.views.generic.detail import (BaseDetailView,
        SingleObjectTemplateResponseMixin)

from comrade.serializers import UniversalJSONSerializer

class JSONResponseMixin(object):
    def render_to_response(self, context):
        """Returns a JSON response containing 'context' as payload."""
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        """Construct an `HttpResponse` object."""
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        """Convert the context dictionary into a JSON object"""
        return UniversalJSONSerializer().serialize(context, ensure_ascii=False)

class JSONListView(JSONResponseMixin, BaseListView):
    pass

class JSONDetailView(JSONResponseMixin, BaseDetailView):
    pass

class HybridDetailView(JSONResponseMixin, SingleObjectTemplateResponseMixin,
        BaseDetailView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.is_ajax() or self.request.GET.get('format') == 'json':
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self,
                    context)

class HybridListView(JSONResponseMixin, MultipleObjectTemplateResponseMixin,
        BaseListView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.is_ajax() or self.request.GET.get('format') == 'json':
            return JSONResponseMixin.render_to_response(self, context)
        else:
            return MultiObjectTemplateResponseMixin.render_to_response(self,
                    context)

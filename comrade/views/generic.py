from django import http
from django.core import serializers
from django.views.generic.list import (BaseListView,
        MultipleObjectTemplateResponseMixin)
from django.views.generic.detail import (BaseDetailView,
        SingleObjectTemplateResponseMixin)

from comrade.serializers import UniversalJSONSerializer

class JSONResponseMixin(object):
    def render_to_response(self, context, **httpresponse_kwargs):
        """Returns a JSON response containing 'context' as payload."""
        return self.get_json_response(self.convert_context_to_json(context),
                **httpresponse_kwargs)

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
    def render_to_response(self, context, **response_kwargs):
        # Look for a 'format=json' GET argument
        if self.request.is_ajax() or self.request.GET.get('format') == 'json':
            return JSONResponseMixin.render_to_response(self, context,
                    **response_kwargs)
        else:
            return SingleObjectTemplateResponseMixin.render_to_response(self,
                    context, **response_kwargs)

class HybridListView(JSONResponseMixin, MultipleObjectTemplateResponseMixin,
        BaseListView):
    def render_to_response(self, context, **response_kwargs):
        # Look for a 'format=json' GET argument or CONTENT-TYPE of
        # application/json
        if (self.request.GET.get('format') == 'json' or
                self.request.META.get('CONTENT_TYPE') == 'application/json'):
            return JSONResponseMixin.render_to_response(self, context,
                    **response_kwargs)
        else:
            return MultipleObjectTemplateResponseMixin.render_to_response(self,
                    context, **response_kwargs)

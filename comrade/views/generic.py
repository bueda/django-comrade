from django.http import HttpResponse
from django.shortcuts import redirect
from django.core import serializers
from django.views.generic.list import (BaseListView,
        MultipleObjectTemplateResponseMixin)
from django.views.generic.edit import (BaseFormView, BaseCreateView, FormMixin,
        ModelFormMixin)
from django.views.generic.detail import (BaseDetailView,
        SingleObjectTemplateResponseMixin)

try:
    # Import Piston if it's installed, but don't die if it's not here. Only a
    # limited number of Middleware require it.
    import piston.utils
    
    # Importing this registers translators for the MimeTypes we are using.
    import piston.emitters
except ImportError:
    pass
else:
    piston.emitters.Emitter.register('text/xml', piston.emitters.XMLEmitter,
            'text/xml; charset=utf-8')
    piston.emitters.Emitter.register('application/json',
            piston.emitters.JSONEmitter, 'application/json; charset=utf-8')


class ContentNegotiationMixin(object):
    """Requires the AcceptMiddleware to be enabled."""
    def _determine_accepted_types(self, request):
        type_html = "text/html"
        if type_html in request.accepted_types:
            return []
        return request.accepted_types
        
    def get_api_response(self, context, **kwargs):
        """If the HttpRequest has something besides text/html in its ACCEPT
        header, try and serialize the context and return an HttpResponse.

        This also responds to a ?format=x query parameter.

        Uses Piston's Emitter utility, so Piston is a requirement for now.
        """
        # Look for a 'format=json' GET argument or CONTENT-TYPE of
        # application/json
        accepted_types = self._determine_accepted_types(self.request)
        for accepted_type in accepted_types:
            try:
                emitter, ct = piston.emitters.Emitter.get(accepted_type)
            except ValueError:
                pass
            else:
                srl = emitter(context, {}, None)
                try:
                    stream = srl.render(self.request)
                    if not isinstance(stream, HttpResponse):
                        response = HttpResponse(stream, mimetype=ct, **kwargs)
                    else:
                        response = stream
                    return response
                except piston.utils.HttpStatusCode, e:
                    return e.response


class HybridDetailView(ContentNegotiationMixin,
        SingleObjectTemplateResponseMixin, BaseDetailView):
    """Return an object detail view, either HTML, JSON or XML (depending on the
    ACCEPT HTTP header or ?format=x query parameter.
    """
    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = SingleObjectTemplateResponseMixin.render_to_response(
                    self, context, **kwargs)
        return response


class HybridListView(ContentNegotiationMixin,
        MultipleObjectTemplateResponseMixin, BaseListView):
    """Return an object list view, either HTML, JSON or XML (depending on the
    ACCEPT HTTP header or ?format=x query parameter.
    """
    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = MultipleObjectTemplateResponseMixin.render_to_response(
                    self, context, **kwargs)
        return response


class HybridFormMixin(FormMixin):
    def get_success_response(self, form):
        content_type = self.request.META.get('CONTENT_TYPE')
        if (not self.request.multipart
                and content_type != "application/x-www-form-urlencoded"):
            return HttpResponse(status=201)
        else:
            return redirect(self.get_success_url())

    def form_valid(self, form):
        return self.get_success_response(form)


class HybridModelFormMixin(ModelFormMixin, HybridFormMixin):
    def form_valid(self, form):
        super(HybridModelFormMixin, self).form_valid(form)
        return self.get_success_response(form)


class RelatedObjectCreateMixin(BaseCreateView):
    related_model = None
    context_form_name = None

    def get_context_form_name(self):
        if self.context_form_name:
            return self.context_form_name
        else:
            return self.related_model.__name__.lower() + "_form"

    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data(
                **{self.get_context_form_name(): form,
                    'object_list': self.object_list}), status=400)

    def get_success_url(self):
        """Return the URL of the parent object."""
        return getattr(self.object, self.related_attribute).get_absolute_url()

    def get_form(self, form_class):
        # TODO this might screw up the object instance when re-rendering because
        # of a form validation error
        if self.request.method in ('POST', 'PUT'):
            return form_class(data=self.request.data,
                files=self.request.FILES,
                initial=self.get_initial(),
                instance=self.get_instance(),)
        else:
            return form_class(initial=self.get_initial(),
                    instance=self.get_instance())

class ModelPermissionCheckMixin(object):
    def get_object(self):
        self.object = super(ModelPermissionCheckMixin, self).get_object()
        if not self.object.can_view(self.request.user):
            raise PermissionDenied()
        return self.object

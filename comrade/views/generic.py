from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.core import serializers
from django.core.exceptions import (PermissionDenied, ValidationError,
        ObjectDoesNotExist)
from django.views.generic.list import (BaseListView,
        MultipleObjectTemplateResponseMixin)
from django.views.generic.edit import (BaseFormView, BaseCreateView, FormMixin,
        ModelFormMixin, ProcessFormView)
from django.views.generic.detail import (BaseDetailView,
        SingleObjectTemplateResponseMixin, SingleObjectMixin)

from comrade.utils import extract

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

    api_context_include_keys = set()
    api_context_exclude_keys = set()
    fields = ()

    def get_fields(self):
        return self.fields

    def get_minimal_context_keys(self, context):
        """Returns keys in this order if they are defined: include_keys,
        exclude_keys, original keys. Currently there is no way to use both
        include and exclude.
        """
        if self.api_context_include_keys:
            return self.api_context_include_keys
        elif self.api_context_exclude_keys:
            return set(context.keys()) - self.api_context_exclude_keys
        else:
            return context.keys()

    def get_minimal_context(self, context):
        # TODO this does some extra work if we we want to include all keys -
        # essentially rebuilds the same dict
        return extract(context, self.get_minimal_context_keys(context))

    def get_api_context_data(self, context):
        return self.get_minimal_context(context)

    def get_api_response(self, context, **kwargs):
        """If the HttpRequest has something besides text/html in its ACCEPT
        header, try and serialize the context and return an HttpResponse.

        This also responds to a ?format=x query parameter.

        Uses Piston's Emitter utility, so Piston is a requirement for now.
        """
        accepted_types = self._determine_accepted_types(self.request)
        for accepted_type in accepted_types:
            try:
                emitter, ct = piston.emitters.Emitter.get(accepted_type)
            except ValueError:
                pass
            else:
                srl = emitter(self.get_api_context_data(context), {}, None,
                        self.fields)
                try:
                    stream = srl.render(self.request)
                    if not isinstance(stream, HttpResponse):
                        response = HttpResponse(stream, mimetype=ct, **kwargs)
                    else:
                        response = stream
                    return response
                except piston.utils.HttpStatusCode, e:
                    return e.response

    def _determine_accepted_types(self, request):
        type_html = "text/html"
        if type_html in request.accepted_types:
            return []
        return request.accepted_types


class PKSafeSingleObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.

        Tries to convert the primary key value provided to the proper type.
        """
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get('pk', None)
        if pk is None:
            pk = self.kwargs.get(queryset.model.__name__.lower() + '_pk', None)
        pk = queryset.model._meta.pk.to_python(pk)
        slug = self.kwargs.get('slug', None)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        elif slug is not None:
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        # If none of those are defined, it's an error.
        else:
            raise AttributeError(u"Generic detail view %s must be called with "
                                 u"either an object id or a slug."
                                 % self.__class__.__name__)

        try:
            obj = queryset.get()
        except ObjectDoesNotExist, ValidationError:
            raise Http404(u"No %s found matching the query" %
                          (queryset.model._meta.verbose_name))
        return obj


class PKSafeBaseDetailView(PKSafeSingleObjectMixin, BaseDetailView):
    pass


class HybridDetailView(ContentNegotiationMixin,
        SingleObjectTemplateResponseMixin, PKSafeBaseDetailView):
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
    api_context_exclude_keys = set(['paginator', 'page_obj', 'is_paginated',
            'object_list',])

    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = MultipleObjectTemplateResponseMixin.render_to_response(
                    self, context, **kwargs)
        return response


class HybridEditMixin(object):
    def get_success_response(self, form=None):
        content_type = self.request.META.get('CONTENT_TYPE', '')
        accept_type = self.request.META.get('HTTP_ACCEPT', '')
        api_call = (accept_type and 'text/html' not in accept_type
                or 'application/json' in content_type)
        if api_call:
            if self.request.method == "POST":
                return HttpResponse(status=201)
            else:
                return HttpResponse(status=200)
        else:
            return redirect(self.get_success_url())


class HybridFormMixin(HybridEditMixin, FormMixin):
    def form_valid(self, form):
        return self.get_success_response(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form),
                status=400)


class HybridModelFormMixin(HybridFormMixin, ModelFormMixin):
    def form_valid(self, form):
        self.object = form.save()
        return super(HybridModelFormMixin, self).form_valid(form)

    def get_instance(self):
        return self.get_object()

    def get_form(self, form_class):
        # TODO this might screw up the object instance when re-rendering because
        # of a form validation error
        # TODO this can probably be moved to get_form_kwargs
        if self.request.method in ('POST', 'PUT'):
            return form_class(data=self.request.data,
                files=self.request.FILES,
                initial=self.get_initial(),
                instance=self.get_instance(),)
        else:
            return form_class(initial=self.get_initial(),
                    instance=self.get_instance())


class RelatedObjectCreateMixin(HybridFormMixin, ProcessFormView):
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


class ModelPermissionCheckMixin(object):
    permission_methods = {
        'GET': 'can_view',
        'POST': 'can_edit',
        'PUT': 'can_edit',
        'DELETE': 'can_delete',
    }

    def get_permission_function(self, http_method=None):
        return getattr(self.object,
                self.permission_methods[http_method or self.request.method])

    def get_object(self):
        self.object = super(ModelPermissionCheckMixin, self).get_object()
        if not self.get_permission_function()(self.request.user,
                request=self.request):
            raise PermissionDenied
        return self.object

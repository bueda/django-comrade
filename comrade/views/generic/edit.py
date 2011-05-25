from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic.edit import (FormMixin, ModelFormMixin,
        ProcessFormView, UpdateView)

import json

from detail import PKSafeSingleObjectMixin
from content import ContentNegotiationMixin
from partial import PartialMixin


class HybridEditMixin(ContentNegotiationMixin, PartialMixin):
    """Requires the AcceptMiddleware."""
    def get_success_response_for_partial(self):
        return redirect(self.get_success_url())

    def get_success_response(self, form=None):
        content_type = self.request.META.get('CONTENT_TYPE', '')
        # TODO expand this to include XML when neccessary. Can't just look for
        # *not* text/html because IE will send '*/*' for HTTP_ACCEPT in
        # everything after the first request for a session.
        if self._render_partial():
            return self.get_success_response_for_partial()
        elif ('text/html' not in self.request.accepted_types and
                'application/json' in self.request.accepted_types or
                'application/json' in content_type):
            if self.request.method == "POST":
                status = 201
            else:
                status = 200
            return HttpResponse(
                    json.dumps({'redirect': self.get_success_url()}),
                    content_type='application/json',
                    status=status)
        else:
            return redirect(self.get_success_url())


class HybridFormMixin(HybridEditMixin, FormMixin):
    form_data = None

    def form_valid(self, form):
        return self.get_success_response(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form),
                status=400)

    def get_form_data(self):
        return self.form_data or self.request.data

    def get_form_kwargs(self):
        kwargs = super(HybridFormMixin, self).get_form_kwargs()
        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.get_form_data()
        return kwargs


class HybridModelFormMixin(HybridFormMixin, ModelFormMixin):
    def form_valid(self, form):
        self.object = form.save()
        return super(HybridModelFormMixin, self).form_valid(form)

    def get_form_kwargs(self):
        self.object = self.get_object()
        return super(HybridModelFormMixin, self).get_form_kwargs()


class HybridUpdateView(PKSafeSingleObjectMixin, HybridModelFormMixin,
        UpdateView):
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.get_success_response(None)


class RelatedObjectCreateMixin(HybridFormMixin, ProcessFormView):
    related_model = None
    context_form_name = None

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(RelatedObjectCreateMixin, self).get_form_kwargs()
        self.related_object = self.get_related_object()
        kwargs.update({'instance': self.related_object})
        return kwargs

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

    def form_valid(self, form):
        self.related_object = form.save()
        return super(RelatedObjectCreateMixin, self).form_valid(form)

    def get_success_url(self):
        """Return the URL of the parent object."""
        return self.related_object.get_absolute_url()

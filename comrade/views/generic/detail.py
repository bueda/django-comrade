from django.http import Http404
from django.core.exceptions import (PermissionDenied, ValidationError,
        ObjectDoesNotExist)
from django.views.generic.detail import (BaseDetailView,
        SingleObjectTemplateResponseMixin)

from content import ContentNegotiationMixin
from partial import PartialTemplateResponseMixin


class PKSafeSingleObjectMixin(object):
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
        if slug is None:
            slug = self.kwargs.get(queryset.model.__name__.lower() + '_slug',
                    None)
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
        except (ObjectDoesNotExist, ValidationError):
            raise Http404(u"No %s found matching the query" %
                          (queryset.model._meta.verbose_name))
        return obj


class HybridDetailView(PKSafeSingleObjectMixin, ContentNegotiationMixin,
        SingleObjectTemplateResponseMixin, PartialTemplateResponseMixin,
        BaseDetailView):
    """Return an object detail view, either HTML, JSON or XML (depending on the
    ACCEPT HTTP header or ?format=x query parameter.
    """
    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = SingleObjectTemplateResponseMixin.render_to_response(
                    self, context, **kwargs)
        return response


class ModelPermissionCheckMixin(object):
    """Call a boolean method on the retreived object to check if the requesting
    user has sufficient permissions.

    By default, expects some standard "can_view" and "can_edit" methods to
    exists, and selects the method based on the HTTP verb requested. This can be
    customized by overriding the get_permission_function() method. The method
    selected should accept the user and request object (as an optional
    argument).

    """

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

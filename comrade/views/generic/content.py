from django.http import HttpResponse

from comrade.utils import extract
from comrade.exceptions import BadRequestError

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
    """Return either HTML or an API response based on the request headers.

    This mixin checks the Accept header, and if it's anything besides text/html,
    tries to serialize the context return from the view to the requested format
    (using Piston's serializers).

    The set of context keys to include/exclude can be controlled either by
    changing the api_context_exclude_keys/api_context_include_keys class
    variables or overriding the get_minimal_context() method.

    Requires the AcceptMiddleware to be enabled.

    """

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
        """Return a subset of the context suitable for an API response."""
        return extract(context, self.get_minimal_context_keys(context))

    def get_api_context_data(self, context):
        return self.get_minimal_context(context)

    def get_api_response(self, context, **kwargs):
        """If the HttpRequest has something besides text/html in its ACCEPT
        header, try and serialize the context and return an HttpResponse.

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

    def render_to_response(self, context, **kwargs):
        response = self.get_api_response(context, **kwargs)
        if not response:
            response = super(ContentNegotiationMixin, self
                    ).render_to_response(context, **kwargs)
        return response

    def _determine_accepted_types(self, request):
        """Assume this request will accept HTML if it either explicitly requests
        it, or if it's IE and it's just giving us '*/*' as this isn't the first
        request of the session.

        """
        if ("text/html" in request.accepted_types
                or request.accepted_types == ['*/*']):
            return []
        return request.accepted_types


class BatchJSONMixin(object):
    """Mix this in with one of the generic form views to allow multiple instance
    to be created by POSTing a JSON list of the data for the instances.

    The JSON key is specified by the batch_json_key class variable, or by the
    get_batch_json_key() method.

    Consider a view that accepts data for a new User object, and it expects a
    'email' and 'username' values. Mix in this class, then POST it JSON like so:

        {'list': [
            {'email': "first_email@example.com",
                'username': "first_username"},
            {'email': "second_email@example.com",
                'username': "second_username"}
            ]
        }

    Two users will be created, the same as if two separate HTTP requests were
    made.

    """
    batch_json_key = 'list'

    def get_batch_json_key(self):
        return self.batch_json_key

    def get_batch_json(self, key=None):
        key = key or self.get_batch_json_key()
        batch = self.request.data.get(key)
        if batch is None:
            raise BadRequestError("Unexpected POSTed JSON format")
        return batch

    def post_json(self, request, *args, **kwargs):
        batch = self.get_batch_json()
        form_class = self.get_form_class()
        form = None
        for data in batch:
            self.form_data = data
            form = form_class(**self.get_form_kwargs())
            if not form.is_valid():
                return self.form_invalid(form)
            form.save()
        return self.get_success_response(form)

    def post(self, request, *args, **kwargs):
        content_type = self.request.META.get('CONTENT_TYPE', '')
        if ('application/json' in content_type
                and self.get_batch_json_key() in request.data):
            return self.post_json(request, *args, **kwargs)
        return super(BatchJSONMixin, self).post(request, *args, **kwargs)

from django.http import Http404, HttpResponseNotAllowed

def get_handler_method(request_handler, http_method):
    try:
        handler_method = getattr(request_handler, http_method.lower())
        if callable(handler_method):
            return handler_method
    except AttributeError:
        pass

class RestfulResource:
    http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']

    @classmethod
    def dispatch(cls, request, *args, **kwargs):
        request_handler = cls()

        if request.method in cls.http_methods:
            handler_method = get_handler_method(request_handler, request.method)
            if handler_method:
                return handler_method(request, *args, **kwargs)

        methods = [method for method in cls.http_methods if get_handler_method(request_handler, method)]
        if len(methods) > 0:
            return HttpResponseNotAllowed(methods)
        else:
            raise Http404

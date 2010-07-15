from django.http import Http404, HttpResponseNotAllowed

def _coerce_put_post(request):
    """
    Django doesn't particularly understand REST.
    In case we send data over PUT, Django won't
    actually look at the data and load it. We need
    to twist its arm here.
    
    The try/except abominiation here is due to a bug
    in mod_python. This should fix it.
    """
    if request.method == "PUT":
        # Bug fix: if _load_post_and_files has already been called, for
        # example by middleware accessing request.POST, the below code to
        # pretend the request is a POST instead of a PUT will be too late
        # to make a difference. Also calling _load_post_and_files will result 
        # in the following exception:
        #   AttributeError: You cannot set the upload handlers after the upload
        #     has been processed.
        # The fix is to check for the presence of the _post field which is set 
        # the first time _load_post_and_files is called (both by wsgi.py and 
        # modpython.py). If it's set, the request has to be 'reset' to redo
        # the query value parsing in POST mode.
        if hasattr(request, '_post'):
            del request._post
            del request._files

        try:
            request.method = "POST"
            request._load_post_and_files()
            request.method = "PUT"
        except AttributeError:
            request.META['REQUEST_METHOD'] = 'POST'
            request._load_post_and_files()
            request.META['REQUEST_METHOD'] = 'PUT'
            
        request.PUT = request.POST

def _get_handler_method(request_handler, http_method):
    try:
        handler_method = getattr(request_handler, http_method.lower())
        if callable(handler_method):
            return handler_method
    except AttributeError:
        pass

class RestfulResource:
    http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'TRACE']

    def __call__(self, request, *args, **kwargs):

        _coerce_put_post(request)

        if request.method in self.http_methods:
            handler_method = _get_handler_method(self, request.method)
            if handler_method:
                return handler_method(request, *args, **kwargs)

        methods = [method for method in self.http_methods if
                _get_handler_method(self, method)]
        if len(methods) > 0:
            return HttpResponseNotAllowed(methods)
        else:
            raise Http404

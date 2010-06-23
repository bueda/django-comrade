def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

def authorized(test_func, unauthorized_url=None):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the unauthorized page if it fails. The test should be a
    callable that takes the user object and returns True if the user passes.
    """
    if not unauthorized_url:
        from django.conf import settings
        unauthorized_url = settings.UNAUTHORIZED_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            return HttpResponseRedirect(unauthorized_url, status=401)
        return wraps(view_func,
                assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

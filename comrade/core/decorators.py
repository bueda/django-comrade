from django.utils.decorators import available_attrs
from django.utils.http import urlquote
from django.http import HttpResponse
from django.template import loader, RequestContext

from functools import wraps

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

def authorized(test_func, template_name='401.html'):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the unauthorized page if it fails. The test should be a
    callable that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user, *args, **kwargs):
                return view_func(request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            t = loader.get_template(template_name)
            return HttpResponse(t.render(RequestContext(request)), status=401)
        return wraps(view_func,
                assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

def admin_login_required(view_func):
    def _decorator(request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            t = loader.get_template('401.html')
            return HttpResponse(t.render(RequestContext(request)), status=401)
    return _decorator


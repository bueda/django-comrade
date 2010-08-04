from django.shortcuts import get_object_or_404
from django.utils.decorators import available_attrs

from comrade.views.simple import direct_to_template

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
            return direct_to_template(template_name, status=401)
        return wraps(view_func,
                assigned=available_attrs(view_func))(_wrapped_view)
    return decorator

def load_instance(model):
    def decorator(view):
        def _wrapper(request, object_id=None, *args, **kwargs):
            if object_id:
                instance = get_object_or_404(model, pk=object_id)
                return view(request, instance, *args, **kwargs)
            return view(request, *args, **kwargs)
        return wraps(view)(_wrapper)
    return decorator

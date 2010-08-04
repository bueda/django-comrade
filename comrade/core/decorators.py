from django.shortcuts import get_object_or_404
from django.utils.decorators import available_attrs
from django.utils.decorators import decorator_from_middleware_with_args

from comrade.core.middleware import PermissionRedirectMiddleware

from functools import wraps

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

def load_instance(model):
    def decorator(view):
        def _wrapped(request, object_id=None, *args, **kwargs):
            if object_id:
                instance = get_object_or_404(model, pk=object_id)
                return view(request, instance, *args, **kwargs)
            return view(request, *args, **kwargs)
        return wraps(view, assigned=available_attrs(view))(_wrapped)
    return decorator

authorized = decorator_from_middleware_with_args(PermissionRedirectMiddleware)

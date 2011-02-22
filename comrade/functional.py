def lazy(func):
    def lazy_func(self, *args, **kwargs):
        cached_attribute = '_cached_%s' % func.__name__
        if not hasattr(self, cached_attribute):
            setattr(self, cached_attribute, func(self, *args, **kwargs))
        return getattr(self, cached_attribute)
    return lazy_func

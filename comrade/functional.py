from functools import wraps

def lazy(func):
    def lazy_func(self, *args, **kwargs):
        cached_attribute = '_cached'
        if not hasattr(self, cached_attribute):
            setattr(self, cached_attribute, {})
        if func.__name__ not in getattr(self, cached_attribute):
            getattr(self, cached_attribute)[func.__name__] = func(
                    self, *args, **kwargs)
        return getattr(self, cached_attribute)[func.__name__]
    return wraps(func)(lazy_func)


def memoize(func):
    def wrapper(self, *args, **kwargs):
        mem_args = kwargs.items()
        mem_args += ('args', args)
        mem_args = tuple(mem_args)

        memoized_attribute = '_memoized'
        if not hasattr(self, memoized_attribute):
            setattr(self, memoized_attribute, {})

        memoized_cache = getattr(self, memoized_attribute)
        memoized_key = func.__name__
        memoized_cache.setdefault(memoized_key, {})
        if mem_args not in memoized_cache[memoized_key]:
            result = func(self, *args, **kwargs)
            memoized_cache[memoized_key][mem_args] = result
        return memoized_cache[memoized_key][mem_args]
    return wraps(func)(wrapper)

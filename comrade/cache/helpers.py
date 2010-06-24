from cache import cache

def check_cache(key):
    cached = cache.get(key)
    if cached is not None:
        cache.set(key, cached)
        return cached

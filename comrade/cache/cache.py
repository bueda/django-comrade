"""
Django Caching Framework wrapper.

Christopher Peplin, peplin@bueda.com

Use these functions instead of directly acessing django.core.cache
and your cache activity will be logged, and keys will be made Memcached-safe
with urlquote.
"""

from django.core.cache import cache
from django.utils.http import urlquote

import logging
logger = logging.getLogger('comrade.cache')

MAX_KEY_LENGTH = 250

def add(key, value, timeout=None):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Adding %s => %s with timeout %d'
            % (key, value, timeout))
    existed = cache.add(key, value, timeout)
    if existed:
        logger.debug('%s was already cached -- not added' % key)
    else:
        logger.debug('%s was not already cached -- added' % key)
    return existed

def get(key, default=None):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Getting %s' % key)
    value = cache.get(key, default)
    if value:
        logger.debug('Found %s for %s' % (value, key))
    else:
        logger.debug('%s not cached' % key)
    return value

def set(key, value, timeout=None):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Setting %s => %s' % (key, value))
    cache.set(key, value, timeout)

def delete(key):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Deleting %s' % key)
    cache.delete(key)

def has_key(key):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Looking for %s' % key)
    exists = cache.has_key(key)
    if exists:
        logger.debug('%s is cached' % key)
    else:
        logger.debug('%s is not cached' % key)
    return exists

def incr(key, delta=1, start=0):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Incremeting %s by %d' % (key, delta))
    if not cache.has_key(key):
        cache.set(key, start + delta)
        return start + delta
    else:
        return cache.incr(key, delta)

def decr(key, delta=1):
    key = urlquote(key)[:MAX_KEY_LENGTH]
    logger.debug('Decrementing %s by %d' % (key, delta))
    return cache.decr(key, delta)

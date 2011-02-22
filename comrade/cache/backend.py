"""
Django Caching Framework wrapper.

Christopher Peplin, peplin@bueda.com

Use these functions instead of directly acessing django.core.cache
and your cache activity will be logged, and keys will be made Memcached-safe
with urlquote.
"""

from django.core.cache import cache
from django.utils.http import urlquote
import hashlib

import commonware.log
logger = commonware.log.getLogger(__name__)

MAX_KEY_LENGTH = 250

class ComradeCacheWrapper(object):
    def _clean_key(self, key):
        key = urlquote(key)
        if len(key) > MAX_KEY_LENGTH:
            hashed_key = hashlib.sha1(key).hexdigest()
            logger.debug('Hashing key %s to %s as it is of len %d (max %d)'
                    % (key, hashed_key, len(key), MAX_KEY_LENGTH))
            key = hashed_key
        return key

    def add(self, key, value, timeout=None):
        key = self._clean_key(key)
        logger.debug('Adding %s => %s with timeout %d'
                % (key, value, timeout))
        existed = cache.add(key, value, timeout)
        if existed:
            logger.debug('%s was already cached -- not added' % key)
        else:
            logger.debug('%s was not already cached -- added' % key)
        return existed

    def get(self, key, default=None):
        key = self._clean_key(key)
        logger.debug('Getting %s' % key)
        value = cache.get(key, default)
        if value is not None:
            logger.debug('Found %s for %s -- touching it' % (value, key))
            cache.set(key, value)
        else:
            logger.debug('%s not cached' % key)
        return value

    def set(self, key, value, timeout=None):
        key = self._clean_key(key)
        logger.debug('Setting %s => %s' % (key, value))
        cache.set(key, value, timeout)

    def delete(self, key):
        key = self._clean_key(key)
        logger.debug('Deleting %s' % key)
        cache.delete(key)

    def has_key(self, key):
        key = self._clean_key(key)
        logger.debug('Looking for %s' % key)
        exists = cache.has_key(key)
        if exists:
            logger.debug('%s is cached' % key)
        else:
            logger.debug('%s is not cached' % key)
        return exists
    __contains__ = has_key

    def incr(self, key, delta=1, start=0):
        key = self._clean_key(key)
        logger.debug('Incremeting %s by %d' % (key, delta))
        if not cache.has_key(key):
            cache.set(key, start + delta)
            return start + delta
        else:
            return cache.incr(key, delta)

    def decr(self, key, delta=1):
        key = self._clean_key(key)
        logger.debug('Decrementing %s by %d' % (key, delta))
        return cache.decr(key, delta)

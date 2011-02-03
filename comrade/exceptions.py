"""
Custom Python exceptions.

Any exception inheriting from ComradeError will be caught by the API error
handler and returned as HttpResponseForbidden or another specific error. Any
exception not in the ComradeError hierarchy will result in an Internal
Server Error.
"""

from django.conf import settings

class ComradeError(Exception):
    def __init__(self, reason):
        super(ComradeError, self).__init__()
        self.reason = reason
        self.name = 'General Error'

    def __unicode__(self):
        return u'%s(%s)' % (self.name, self.reason)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

class BadRequestError(ComradeError):
    def __init__(self, reason):
        super(BadRequestError, self).__init__(reason)
        self.name = 'Bad Request'

class HttpResponseError(ComradeError):
    def __init__(self, reason, url, response):
        super(HttpResponseError, self).__init__(reason)
        self.name = 'HTTP Exception'
        self.url = url
        self.response = response

    def __unicode__(self):
        return u'%s(%s, URL: %s, Response: %s)' % (self.name, self.reason,
                self.url, self.response)

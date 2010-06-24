"""
Custom Python exceptions.

Any exception inheriting from ComradeException will be caught by the API error
handler and returned as HttpResponseForbidden or another specific error. Any
exception not in the ComradeException hierarchy will result in an Internal
Server Error.
"""

from django.conf import settings

class ComradeException(Exception):
    def __init__(self, reason):
        super(ComradeException, self).__init__()
        self.reason = reason
        self.name = 'General Error'

    def __unicode__(self):
        return '%s(%s)' % (self.name, self.reason)

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

class BadRequestException(ComradeException):
    def __init__(self, reason):
        super(BadRequestException, self).__init__(reason)
        self.name = 'Bad Request'

class HttpResponseException(ComradeException):
    def __init__(self, reason, url, response):
        super(HttpResponseException, self).__init__(reason)
        self.name = 'HTTP Exception'
        self.url = url
        self.response = response

    def __unicode__(self):
        return '%s(%s, URL: %s, Response: %s)' % (self.name, self.reason,
                self.url, self.response)

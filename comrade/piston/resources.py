from piston.resource import PistonResource
from django.http import HttpResponseServerError, HttpResponseBadRequest

from comrade.exceptions import (ComradeException, HttpResponseException, 
        BadRequestException)

import commonware.log
logger = commonware.log.getLogger('comrade.piston.resources')

class Resource(PistonResource):
    def error_handler(self, error, request, method):
        if isinstance(error, ComradeException):
            logger.error(u'%s' % error)
            return _handle_comrade_exception(error)
        logger.exception(u'%s' % error)
        return super(Resource, self).error_handler(error, request, method)

class DebugResource(PistonResource):
    def error_handler(self, error, request, method):
        logger.exception(u'%s' % error)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            raise
        elif isinstance(error, ComradeException):
            return _handle_comrade_exception(error)
        else:
            error.name = 'Unhandled exception'
            error.reason = str(error)
            return HttpResponseServerError(
                    content=_json_error(error))

def _json_error(error):
    response = dict(name=error.name,
            reason=error.reason,
            success=False)
    return response

def _handle_comrade_exception(error):
    if isinstance(error, HttpResponseException):
        return HttpResponseServerError(
                content=_json_error(error))
    elif isinstance(error, BadRequestException):
        return HttpResponseBadRequest(
                content=_json_error(error))
    else:
        return HttpResponseServerError(
                content=_json_error(error))
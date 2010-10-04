from piston.resource import Resource as PistonResource
from django.http import HttpResponseServerError, HttpResponseBadRequest

from comrade.exceptions import (ComradeError, HttpResponseError, 
        BadRequestError)

import commonware.log
logger = commonware.log.getLogger(__name__)

class Resource(PistonResource):
    def error_handler(self, error, request, method):
        if isinstance(error, ComradeError):
            logger.error(u'%s' % error)
            return _handle_comrade_exception(error)
        logger.exception(u'%s' % error)
        return super(Resource, self).error_handler(error, request, method)

class DebugResource(PistonResource):
    def error_handler(self, error, request, method):
        logger.exception(u'%s' % error)
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            raise
        elif isinstance(error, ComradeError):
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
    if isinstance(error, HttpResponseError):
        return HttpResponseServerError(
                content=_json_error(error))
    elif isinstance(error, BadRequestError):
        return HttpResponseBadRequest(
                content=_json_error(error))
    else:
        return HttpResponseServerError(
                content=_json_error(error))

from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson
from django.utils.encoding import smart_unicode
from django.db.models import Model

from comrade.serializers import UniversalJSONSerializer

class HttpJsonResponse(HttpResponse):
    def __init__(self, context, status=None):
        content = UniversalJSONSerializer().serialize(context)
        super(HttpJsonResponse, self).__init__(
                content, content_type='application/json', status=status)

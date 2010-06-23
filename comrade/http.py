from django.core.serializers import json, serialize
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.utils import simplejson

class HttpJsonResponse(HttpResponse):
    def __init__(self, object, status=None):
        if isinstance(object, QuerySet):
            content = serialize('json', object)
        else:
            content = simplejson.dumps(object, cls=json.DjangoJSONEncoder,
                ensure_ascii=False)
        super(HttpJsonResponse, self).__init__(
                content, content_type='application/json')

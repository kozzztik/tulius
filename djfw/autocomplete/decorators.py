import json
import sys

from django.utils.decorators import wraps
from django.http import HttpResponse
from django.http import Http404


def autocomplete_result(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        name = request.REQUEST.get('q', None)
        if not name:
            raise Http404()
        limit = int(request.REQUEST.get('limit', 10))
        if limit > 40:
            limit = 40
        args = (request, ) + args + (name, limit)
        try:
            items = func(*args, **kwargs)
        except:
            return HttpResponse('CACHE_MISS ' + str(sys.exc_info()))
        result = []
        for item in items:
            result.append((item.id, str(item)))
        return HttpResponse(json.dumps(result))
    return inner

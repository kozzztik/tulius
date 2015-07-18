from django.utils.decorators import wraps
from django.http import HttpResponse
from django.utils import simplejson
from django.http import Http404
import sys

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
            return HttpResponse('CACHE_MISS ' +  unicode(sys.exc_info()))
        result = []
        for item in items:
            result.append((item.id, str(item)))
        return HttpResponse(simplejson.dumps(result))
    return inner

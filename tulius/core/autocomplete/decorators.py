import json
import functools

from django import http


def autocomplete_result(func):
    @functools.wraps(func)
    def inner(request, *args, **kwargs):
        name = request.GET.get('q', None)
        if not name:
            raise http.Http404()
        limit = int(request.GET.get('limit', 10))
        limit = min(limit, 40)
        args = (request, ) + args + (name, limit)
        items = func(*args, **kwargs)
        result = []
        for item in items:
            result.append((item.id, str(item)))
        return http.HttpResponse(json.dumps(result))
    return inner

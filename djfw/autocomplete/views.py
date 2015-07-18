from django.contrib.auth import get_user_model
from .decorators import autocomplete_result
from django.conf import settings

@autocomplete_result
def autocomplete_user(request, name, limit):  
    users = get_user_model().objects.filter(username__istartswith=name)[:limit]
    return users
    
import pickle
from django.db.models.query import QuerySet
from django.db.models import get_model
from django.http import Http404
from .monkey import _queryset_cache
from .utils import get_search_fieldname
import sys

@autocomplete_result
def get_autocomplete(request, name, limit, token):
    """Return matching results as JSON"""
    if len(name) < 3:
        raise Http404()
    pickled = _queryset_cache.get(token, None)
    if pickled is None:
        raise Http404(unicode(sys.exc_info()))
    app_label, model_name, query = pickle.loads(pickled)
    auth_format = '%s.%s' % (app_label, model_name)
    auth_model = getattr(settings, 'AUTH_USER_MODEL', '').lower()
    if auth_format == auth_model:
        model = get_user_model()
        fieldname = getattr(model, 'USERNAME_FIELD', None)
        if fieldname:
            di = {'%s__istartswith' % fieldname: name}
            return model.objects.filter(**di).order_by(fieldname)[:limit]
    model = get_model(app_label, model_name)
    queryset = QuerySet(model=model, query=query)
    fieldname = get_search_fieldname(model)
    di = {'%s__istartswith' % fieldname: name}
    return queryset.filter(**di).order_by(fieldname)[:limit]
    
import pickle
import sys

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.http import Http404

from tulius.core.autocomplete import decorators
from tulius.core.autocomplete import models


@decorators.autocomplete_result
def autocomplete_user(request, name, limit):
    users = get_user_model().objects.filter(username__istartswith=name)[:limit]
    return users


@decorators.autocomplete_result
def get_autocomplete(request, name, limit, token):
    """Return matching results as JSON"""
    if len(name) < 3:
        raise Http404()
    pickled = models.queryset_cache.get(token, None)
    if pickled is None:
        raise Http404(str(sys.exc_info()))
    app_label, model_name, query, field_name = pickle.loads(pickled)
    model = apps.get_model(app_label, model_name)
    queryset = QuerySet(model=model, query=query)
    di = {'%s__istartswith' % field_name: name}
    return queryset.filter(**di).order_by(field_name)[:limit]

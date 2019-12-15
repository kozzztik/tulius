import pickle
import hashlib

from .widget import AutocompleteWidget

queryset_cache = {}


def add_autocomplete_widget(model, queryset, field_name):
    pickled = pickle.dumps((
        model._meta.app_label,
        model._meta.object_name,
        queryset.query,
        field_name
    ))
    token = hashlib.md5(pickled).hexdigest()
    queryset_cache[token] = pickled
    return AutocompleteWidget(queryset.model, token)

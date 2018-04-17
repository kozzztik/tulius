import pickle
import hashlib

from django.forms.models import ModelChoiceField, ModelMultipleChoiceField
from django.conf import settings
from django.forms.fields import Field

from .widget import AutocompleteWidget

_queryset_cache = {}


def ModelChoiceField__init__(
        self, queryset, empty_label=u"---------",
        cache_choices=False, required=True, widget=None, label=None,
        initial=None, help_text=None, to_field_name=None, *args, **kwargs):
    if required and (initial is not None):
        self.empty_label = None
    else:
        self.empty_label = empty_label
    self.cache_choices = cache_choices

    # Monkey starts here
    if self.__class__ in (ModelChoiceField, ModelMultipleChoiceField):
        meta = queryset.model._meta
        module_name = queryset.model.__module__
        module_name = module_name.split('.')[-1]
        key = '%s.%s' % (meta.app_label, module_name)
        # Handle both legacy settings SIMPLE_AUTOCOMPLETE_MODELS and new
        # setting SIMPLE_AUTOCOMPLETE.
        models = getattr(
            settings, 'AUTOCOMPLETE_MODELS',
            getattr(settings, 'AUTOCOMPLETE', {}).keys()
        )
        if key in models:
            pickled = pickle.dumps((
                queryset.model._meta.app_label,
                queryset.model._meta.module_name,
                queryset.query
            ))
            token = hashlib.md5(pickled).hexdigest()
            _queryset_cache[token] = pickled
            widget = AutocompleteWidget(queryset.model, token)
            
    # Monkey ends here

    kwargs.pop('limit_choices_to', None)

    # Call Field instead of ChoiceField __init__() because we don't need
    # ChoiceField.__init__().
    Field.__init__(
        self, required=required, widget=widget, label=label, initial=initial,
        help_text=help_text, *args, **kwargs)

    self.queryset = queryset
    self.choice_cache = None
    self.to_field_name = to_field_name


ModelChoiceField.__init__ = ModelChoiceField__init__

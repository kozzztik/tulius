import json
import logging
import datetime
from logging import handlers

from django.apps import apps
from django.conf import settings
from django.db import models
from django.db.models import signals
from django.db.models.fields import related
from django.db.models.fields import reverse_related

logger = logging.getLogger('elastic_search_indexing')


def index_name(model):
    s = f"{model._meta.app_label}_{model._meta.object_name}"
    return f"{settings.ELASTIC_PREFIX}_{s}".lower()


ignore_field_types = (
    related.RelatedField,
    reverse_related.ForeignObjectRel,
    models.AutoField,
    models.FileField,
)


def do_index(instance, **_kwargs):
    data = {}
    for field in instance.__class__._meta.get_fields(include_hidden=True):
        if not isinstance(field, ignore_field_types):
            value = getattr(instance, field.name)
            if isinstance(value, datetime.date):
                value = value.isoformat()
            data[field.column] = value
    if hasattr(instance, 'to_elastic_search'):
        instance.to_elastic_search(data)
    data['pk'] = instance.pk
    data['message'] = index_name(instance.__class__)
    record = bytes(json.dumps(data), 'utf-8')
    for h in logger.handlers:
        if isinstance(h, (handlers.SocketHandler, handlers.DatagramHandler)):
            h.send(record)


def init():
    for app_name, model_name in settings.ELASTIC_MODELS:
        model = apps.get_model(app_name, model_name)
        signals.post_save.connect(do_index, sender=model, weak=False)

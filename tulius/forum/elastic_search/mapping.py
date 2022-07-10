from elasticsearch7 import exceptions
from django.db import models

from tulius.forum.elastic_search import models as elastic_models


field_descriptors = {
    models.IntegerField: {'type': 'integer'},
    models.SmallIntegerField: {'type': 'integer'},
    models.PositiveIntegerField: {'type': 'long'},
    models.DateTimeField: {'type': 'date'},
    models.CharField: {'type': 'text'},
    models.TextField: {'type': 'text'},
    models.BooleanField: {'type': 'boolean'},
    models.JSONField: {'properties': {}},
    models.EmailField: {'type': 'keyword'},
}


def rebuild_index(model):
    fields = {}
    for field in model._meta.get_fields(include_hidden=True):
        if not isinstance(field, elastic_models.ignore_field_types):
            fields[field.column] = field_descriptors[field.__class__]
    if hasattr(model, 'to_elastic_mapping'):
        model.to_elastic_mapping(fields)
    index_name = elastic_models.index_name(model)
    try:
        elastic_models.client.indices.delete(index_name)
    except exceptions.NotFoundError:
        pass
    elastic_models.client.indices.create(index_name, body={
        'mappings': {
            'properties': fields
        }
    })

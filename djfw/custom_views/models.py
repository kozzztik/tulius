from django.db import models


class SortableModelMixin(models.Model):
    class Meta:
        abstract = True
        ordering = ['order', 'id']

    order = models.IntegerField(
        default=0,
        blank=False,
        null=False,
        editable=False
    )

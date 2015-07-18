# -*- coding: utf-8 -*-

from django.db import models
from django import forms
from django.utils.text import capfirst
from django.conf import settings


from colors.widgets import ColorPickerWidget

class ColorField(models.CharField):
	def __init__(self, *args, **kwargs):
		kwargs['max_length'] = 7
		super(ColorField, self).__init__(*args, **kwargs)

	def formfield(self, **kwargs):
		kwargs['widget'] = ColorPickerWidget
		return super(ColorField, self).formfield(**kwargs)

try:
	from south.modelsinspector import add_introspection_rules
	add_introspection_rules([], ["^colors\.fields\.ColorField"])
except ImportError:
	pass
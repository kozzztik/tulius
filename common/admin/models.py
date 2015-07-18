# -*- coding: utf-8 -*-

# AlphabeticFilterSpec: see http://djangosnippets.org/snippets/1051/
# Authors: Marinho Brandao <marinho at gmail.com>
#          Guilherme M. Gondim (semente) <semente at taurinus.org>
# File: <your project>/admin/filterspecs.py

#from django.db import models
from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec#, RelatedFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _

class AlphabeticFilterSpec(ChoicesFilterSpec):
	"""
		Adds filtering by first char (alphabetic style) of values in the admin
		filter sidebar. Set the alphabetic filter in the model field attribute
		'alphabetic_filter'.

		my_model_field.alphabetic_filter = True
		"""

	def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
		super(AlphabeticFilterSpec, self).__init__(f, request, params, model,
			model_admin, *args, **kwargs)
		self.lookup_kwarg = '%s__istartswith' % f.name
		self.lookup_val = request.GET.get(self.lookup_kwarg, None)
		values_list = model.objects.values_list(f.name, flat=True)
		# getting the first char of values
		self.lookup_choices = list(set(val[0] for val in values_list if val))
		self.lookup_choices.sort()

	def choices(self, cl):
		yield {'selected': self.lookup_val is None,
		       'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
		       'display': _('All')}
		for val in self.lookup_choices:
			yield {'selected': smart_unicode(val) == self.lookup_val,
			       'query_string': cl.get_query_string({self.lookup_kwarg: val}),
			       'display': val.upper()}
	def title(self):
		return _('%(field_name)s that starts with') %\
		       {'field_name': self.field.verbose_name}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'alphabetic_filter', False),
                                   AlphabeticFilterSpec))

from django.contrib.admin.util import reverse_field_path

#class ManagerFilterSpec(RelatedFilterSpec):
#	def __init__(self, f, request, params, model, model_admin,
#	             field_path='id'):
#		super(ManagerFilterSpec, self).__init__(f, request, params, model,
#			model_admin, field_path=field_path)
#		if request.user.is_superuser:
#			parent_model, reverse_path = reverse_field_path(model, self.field_path)
#			queryset = parent_model._default_manager.all()
#			self.lookup_choices = [(user.id, user.__unicode__()) for user in queryset.filter(is_staff=True)]
#		else:
#			self.lookup_choices = [(request.user.id, request.user.__unicode__()),]
#
#
## registering the filter
#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'manager_filter', False),
#                                   ManagerFilterSpec))

#class CurrentManagerUserFilterSpec(RelatedFilterSpec):
#	def __init__(self, f, request, params, model, model_admin,
#	             field_path='id'):
#		super(CurrentManagerUserFilterSpec, self).__init__(
#			f, request, params, model, model_admin, field_path=field_path)
#		if request.user.is_superuser:
#			return
#		parent_model, reverse_path = reverse_field_path(model, self.field_path)
#		queryset = parent_model._default_manager.all()
#		self.lookup_choices = [(user.id, user.__unicode__())\
#		for user in queryset.filter(manager=request.user)]
#
#
## registering the filter
#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'current_manager_user_filter', False),
#                                   CurrentManagerUserFilterSpec))


#class CurrentManagerUserOrdersFilterSpec(RelatedFilterSpec):
#	def __init__(self, f, request, params, model, model_admin,
#	             field_path='id'):
#		super(CurrentManagerUserOrdersFilterSpec, self).__init__(
#			f, request, params, model, model_admin, field_path=field_path)
#		if request.user.is_superuser:
#			return
#		parent_model, reverse_path = reverse_field_path(model, self.field_path)
#		queryset = parent_model._default_manager.all()
#		self.lookup_choices = [(order.id, order.__unicode__())\
#		for order in queryset.filter(user__manager=request.user)]
#
#
## registering the filter
#FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'current_manager_user_orders_filter', False),
#                                   CurrentManagerUserOrdersFilterSpec))


#TODO: merge with CategoryIsSetFilterSpec
class ImageIsSetFilterSpec(FilterSpec):
	def __init__(self, f, request, params, model, model_admin, field_path=None):
		super(ImageIsSetFilterSpec, self).__init__(f, request,
			params, model, model_admin, field_path)

	def choices(self, cl):
		return [
			#{
			#	'selected': self.lookup_val is None,
			#	'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
			#	'display': _('All')
			#},
				{
				'selected': False,#self.lookup_val is 'True',
				'query_string': '?image__isnull=False',
				'display': _(u'Установлено')
			},
				{
				'selected': False,#self.lookup_val is 'False',
				'query_string': '?image__isnull=True',
				'display': _(u'Не установлено')
			}
		]

#TODO: merge with ImageIsSetFilterSpec
class CategoryIsSetFilterSpec(FilterSpec):
	def __init__(self, f, request, params, model, model_admin, field_path=None):
		super(CategoryIsSetFilterSpec, self).__init__(f, request,
			params, model, model_admin, field_path)

	def choices(self, cl):
		return [
			#{
			#	'selected': self.lookup_val is None,
			#	'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
			#	'display': _('All')
			#},
				{
				'selected': False,#self.lookup_val is 'True',
				'query_string': '?category__isnull=False',
				'display': _(u'Установлена')
			},
				{
				'selected': False,#self.lookup_val is 'False',
				'query_string': '?category__isnull=True',
				'display': _(u'Не установлена')
			}
		]

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'image_is_set_filter', False),
                                   ImageIsSetFilterSpec))

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'category_is_set_filter', False),
                                   CategoryIsSetFilterSpec))
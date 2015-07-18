# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.signals import post_save

class DirtyFieldsMixin(object):
	
	def __init__(self, *args, **kwargs):
		super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
		post_save.connect(
			self._reset_state,
			sender = self.__class__,
			dispatch_uid = '%s-DirtyFieldsMixin-sweeper' % self.__class__.__name__
		)
		self._reset_state()

	def _reset_state(self, *args, **kwargs):
		self._original_state = self._as_dict()

	def _as_dict(self):
		return dict([(f.attname, getattr(self, f.attname)) for f in self._meta.local_fields])

	def get_dirty_fields(self):
		new_state = self._as_dict()
		return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])

class UpdatedAndCreatedDatesMixin(models.Model):
	
	class Meta:
		abstract			= True
		ordering			= ['-updated_at']
	
	updated_at = models.DateTimeField(
		auto_now		= True,
		verbose_name	= _('updated at'),
#		editable		= False,
	)
	created_at = models.DateTimeField(
		auto_now_add	= True,
		verbose_name	= _('created at'),
#		editable		= False,
	)

class SortableMixin(models.Model):
	class Meta:
		abstract = True
		ordering = ['position']
	position = models.PositiveSmallIntegerField(_("Position"), blank=True, null=True)

class AbstractBaseModel(UpdatedAndCreatedDatesMixin, SortableMixin):
	class Meta(UpdatedAndCreatedDatesMixin.Meta, SortableMixin.Meta):
		abstract	= True
		ordering = ['position']
		
class AbstractStatusModel(AbstractBaseModel):
	
	class Meta(AbstractBaseModel.Meta):
		verbose_name		= _('status')
		verbose_name_plural = _('statuses')
		abstract			= True
	
	name = models.CharField(
		max_length			= 200,
		default				= '',
		blank				= False,
		null				= False,
		verbose_name		= _('name')
	)
	
	def __unicode__(self):
		return '#%s. %s' % (self.id, self.name,)
	
class AbstractDescribedStatusModel(AbstractStatusModel):
	
	class Meta(AbstractBaseModel.Meta):
		verbose_name		= _('described status')
		verbose_name_plural = _('described statuses')
		abstract			= True
	
	description = models.TextField(
		null				= True,
		blank				= True,
		default				= '',
		verbose_name		= _(u'Описание')
	)
	
class AbstractMessage(AbstractBaseModel):
	
	class Meta(AbstractBaseModel.Meta):
		verbose_name		= _('message')
		verbose_name_plural = _('messages')
		abstract			= True
	
	title = models.CharField(
		max_length			= 200,
		unique				= False,
		verbose_name		= _('title')
	)
	body = models.TextField(
		null				= True,
		blank				= True,
		default				= '',
		verbose_name		= _('body')
	)	
	
	def __unicode__(self):
		return '#%s. %s' % (self.id, self.title,)

class AbstractQuestion(AbstractBaseModel):
	class Meta(AbstractBaseModel.Meta):
		verbose_name = _('question')
		verbose_name_plural = _('questions')
		abstract=True

	body = models.TextField(
		default='',
		verbose_name=_(u'body')
	)

	def __unicode__(self):
		return u'%s' % (self.body)
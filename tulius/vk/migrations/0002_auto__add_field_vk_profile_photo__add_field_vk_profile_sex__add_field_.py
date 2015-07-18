# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'VK_Profile.photo'
        db.add_column(u'vk_vk_profile', 'photo',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'VK_Profile.sex'
        db.add_column(u'vk_vk_profile', 'sex',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'VK_Profile.access_token'
        db.add_column(u'vk_vk_profile', 'access_token',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'VK_Profile.token_expires'
        db.add_column(u'vk_vk_profile', 'token_expires',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'VK_Profile.photo'
        db.delete_column(u'vk_vk_profile', 'photo')

        # Deleting field 'VK_Profile.sex'
        db.delete_column(u'vk_vk_profile', 'sex')

        # Deleting field 'VK_Profile.access_token'
        db.delete_column(u'vk_vk_profile', 'access_token')

        # Deleting field 'VK_Profile.token_expires'
        db.delete_column(u'vk_vk_profile', 'token_expires')


    models = {
        u'vk.vk_profile': {
            'Meta': {'object_name': 'VK_Profile'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'photo': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'token_expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'vk_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['vk']
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'VK_Profile'
        db.create_table(u'vk_vk_profile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('vk_id', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal(u'vk', ['VK_Profile'])


    def backwards(self, orm):
        # Deleting model 'VK_Profile'
        db.delete_table(u'vk_vk_profile')


    models = {
        u'vk.vk_profile': {
            'Meta': {'object_name': 'VK_Profile'},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'vk_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        }
    }

    complete_apps = ['vk']
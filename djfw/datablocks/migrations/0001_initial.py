# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DataBlock'
        db.create_table('datablocks_datablock', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('full_text', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('urls', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('exclude_urls', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
        ))
        db.send_create_signal('datablocks', ['DataBlock'])


    def backwards(self, orm):
        # Deleting model 'DataBlock'
        db.delete_table('datablocks_datablock')


    models = {
        'datablocks.datablock': {
            'Meta': {'object_name': 'DataBlock'},
            'exclude_urls': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'urls': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['datablocks']
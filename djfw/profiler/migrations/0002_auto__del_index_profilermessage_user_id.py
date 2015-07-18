# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.delete_foreign_key(u'profiler_profilermessage', 'user_id')
        # Removing index on 'ProfilerMessage', fields ['user_id']
        db.delete_index(u'profiler_profilermessage', ['user_id'])


    def backwards(self, orm):
        # Adding index on 'ProfilerMessage', fields ['user_id']
        db.create_index(u'profiler_profilermessage', ['user_id'])


    models = {
        'profiler.profilermessage': {
            'Meta': {'ordering': "['module_name', 'func_name', '-id']", 'object_name': 'ProfilerMessage'},
            'browser': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'browser_version': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_count': ('django.db.models.fields.BigIntegerField', [], {}),
            'db_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'device': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'error': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exec_param': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exec_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'func_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mobile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'module_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'os_version': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'template_db_count': ('django.db.models.fields.BigIntegerField', [], {}),
            'template_db_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'template_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['profiler']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ProfilerMessage.thread_id'
        db.add_column('profiler_profilermessage', 'thread_id',
                      self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding index on 'ProfilerMessage', fields ['create_time']
        db.create_index('profiler_profilermessage', ['create_time'])


    def backwards(self, orm):
        # Removing index on 'ProfilerMessage', fields ['create_time']
        db.delete_index('profiler_profilermessage', ['create_time'])

        # Deleting field 'ProfilerMessage.thread_id'
        db.delete_column('profiler_profilermessage', 'thread_id')


    models = {
        'profiler.profilermessage': {
            'Meta': {'ordering': "['module_name', 'func_name', '-id']", 'object_name': 'ProfilerMessage'},
            'browser': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'browser_version': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
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
            'thread_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['profiler']
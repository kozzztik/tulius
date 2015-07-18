# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ProfilerMessage'
        db.create_table(u'profiler_profilermessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('module_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, db_index=True, blank=True)),
            ('func_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, db_index=True, blank=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user_id', self.gf('django.db.models.fields.BigIntegerField')(blank=True, db_index=True, null=True)),
            ('exec_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('db_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('db_count', self.gf('django.db.models.fields.BigIntegerField')()),
            ('template_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('template_db_time', self.gf('django.db.models.fields.BigIntegerField')()),
            ('template_db_count', self.gf('django.db.models.fields.BigIntegerField')()),
            ('exec_param', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('browser', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('browser_version', self.gf('django.db.models.fields.CharField')(default='', max_length=10, null=True, blank=True)),
            ('os', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('os_version', self.gf('django.db.models.fields.CharField')(default='', max_length=10, null=True, blank=True)),
            ('device', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('mobile', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('error', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'profiler', ['ProfilerMessage'])


    def backwards(self, orm):
        # Deleting model 'ProfilerMessage'
        db.delete_table(u'profiler_profilermessage')


    models = {
        u'profiler.profilermessage': {
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
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'mobile': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'module_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'os': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'os_version': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'template_db_count': ('django.db.models.fields.BigIntegerField', [], {}),
            'template_db_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'template_time': ('django.db.models.fields.BigIntegerField', [], {}),
            'user_id': ('django.db.models.fields.BigIntegerField', [], {'blank': 'True', 'null': 'True', 'db_index': "True"})
        },
    }

    complete_apps = ['profiler']
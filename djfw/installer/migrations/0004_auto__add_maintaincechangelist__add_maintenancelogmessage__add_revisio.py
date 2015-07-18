# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MaintainceChangelist'
        db.create_table('installer_maintaincechangelist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mainteince', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['installer.MaintenanceLog'])),
            ('revision', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['installer.Revision'])),
        ))
        db.send_create_signal('installer', ['MaintainceChangelist'])

        # Adding model 'MaintenanceLogMessage'
        db.create_table('installer_maintenancelogmessage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mainteince', self.gf('django.db.models.fields.related.ForeignKey')(related_name='messages', to=orm['installer.MaintenanceLog'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('text', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('installer', ['MaintenanceLogMessage'])

        # Adding model 'Revision'
        db.create_table('installer_revision', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('installer', ['Revision'])


    def backwards(self, orm):
        # Deleting model 'MaintainceChangelist'
        db.delete_table('installer_maintaincechangelist')

        # Deleting model 'MaintenanceLogMessage'
        db.delete_table('installer_maintenancelogmessage')

        # Deleting model 'Revision'
        db.delete_table('installer_revision')


    models = {
        'installer.backup': {
            'Meta': {'object_name': 'Backup'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups'", 'to': "orm['installer.BackupCategory']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'installer.backupcategory': {
            'Meta': {'object_name': 'BackupCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'saved_backups': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'installer.maintaincechangelist': {
            'Meta': {'object_name': 'MaintainceChangelist'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainteince': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['installer.MaintenanceLog']"}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['installer.Revision']"})
        },
        'installer.maintenancelog': {
            'Meta': {'object_name': 'MaintenanceLog'},
            'buildout_update_time': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'installer.maintenancelogmessage': {
            'Meta': {'object_name': 'MaintenanceLogMessage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mainteince': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'messages'", 'to': "orm['installer.MaintenanceLog']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''"})
        },
        'installer.revision': {
            'Meta': {'object_name': 'Revision'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['installer']
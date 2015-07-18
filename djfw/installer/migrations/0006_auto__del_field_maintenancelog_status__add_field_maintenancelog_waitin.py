# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'MaintenanceLog.status'
        db.delete_column('installer_maintenancelog', 'status')

        # Adding field 'MaintenanceLog.waiting_user'
        db.add_column('installer_maintenancelog', 'waiting_user',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'MaintenanceLog.operations'
        db.add_column('installer_maintenancelog', 'operations',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'MaintenanceLog.operation'
        db.add_column('installer_maintenancelog', 'operation',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'MaintenanceLog.params'
        db.add_column('installer_maintenancelog', 'params',
                      self.gf('django.db.models.fields.TextField')(default='', max_length=255, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'MaintenanceLog.status'
        db.add_column('installer_maintenancelog', 'status',
                      self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'MaintenanceLog.waiting_user'
        db.delete_column('installer_maintenancelog', 'waiting_user')

        # Deleting field 'MaintenanceLog.operations'
        db.delete_column('installer_maintenancelog', 'operations')

        # Deleting field 'MaintenanceLog.operation'
        db.delete_column('installer_maintenancelog', 'operation')

        # Deleting field 'MaintenanceLog.params'
        db.delete_column('installer_maintenancelog', 'params')


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
            'operation': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'operations': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'waiting_user': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
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
            'time': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['installer']
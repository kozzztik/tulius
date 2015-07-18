# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BackupCategory'
        db.create_table(u'installer_backupcategory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('verbose_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('saved_backups', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'installer', ['BackupCategory'])

        # Adding model 'Backup'
        db.create_table(u'installer_backup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='backups', to=orm['installer.BackupCategory'])),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('size', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'installer', ['Backup'])


    def backwards(self, orm):
        # Deleting model 'BackupCategory'
        db.delete_table(u'installer_backupcategory')

        # Deleting model 'Backup'
        db.delete_table(u'installer_backup')


    models = {
        u'installer.backup': {
            'Meta': {'object_name': 'Backup'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'backups'", 'to': u"orm['installer.BackupCategory']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        u'installer.backupcategory': {
            'Meta': {'object_name': 'BackupCategory'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'saved_backups': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'verbose_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['installer']
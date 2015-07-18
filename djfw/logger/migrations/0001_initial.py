# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.conf import settings

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LogMessage'
        db.create_table(u'logger_logmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('level', self.gf('django.db.models.fields.SmallIntegerField')(default=0, db_index=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('logger_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('module_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'logger', ['LogMessage'])

        # Adding model 'ExceptionMessage'
        db.create_table(u'logger_exceptionmessage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.PositiveIntegerField')(blank=True, null=True, db_index=True)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('classname', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('get_data', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('post_data', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'logger', ['ExceptionMessage'])

        # Adding model 'ExceptionCookie'
        db.create_table(u'logger_exceptioncookie', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exception_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='cookies', to=orm['logger.ExceptionMessage'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'logger', ['ExceptionCookie'])

        # Adding model 'ExceptionMETAValue'
        db.create_table(u'logger_exceptionmetavalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exception_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='metas', to=orm['logger.ExceptionMessage'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'logger', ['ExceptionMETAValue'])

        # Adding model 'ExceptionTraceback'
        db.create_table(u'logger_exceptiontraceback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exception_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='traceback', to=orm['logger.ExceptionMessage'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('line_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('function_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=250)),
        ))
        db.send_create_signal(u'logger', ['ExceptionTraceback'])


    def backwards(self, orm):
        # Deleting model 'LogMessage'
        db.delete_table(u'logger_logmessage')

        # Deleting model 'ExceptionMessage'
        db.delete_table(u'logger_exceptionmessage')

        # Deleting model 'ExceptionCookie'
        db.delete_table(u'logger_exceptioncookie')

        # Deleting model 'ExceptionMETAValue'
        db.delete_table(u'logger_exceptionmetavalue')

        # Deleting model 'ExceptionTraceback'
        db.delete_table(u'logger_exceptiontraceback')


    models = {
        u'logger.exceptioncookie': {
            'Meta': {'ordering': "['name']", 'object_name': 'ExceptionCookie'},
            'exception_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cookies'", 'to': u"orm['logger.ExceptionMessage']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'logger.exceptionmessage': {
            'Meta': {'ordering': "['-id']", 'object_name': 'ExceptionMessage'},
            'classname': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'get_data': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post_data': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'exceptions'", 'null': 'True', 'to': u"orm['" + settings.AUTH_USER_MODEL + "']"})
        },
        u'logger.exceptionmetavalue': {
            'Meta': {'ordering': "['name']", 'object_name': 'ExceptionMETAValue'},
            'exception_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'metas'", 'to': u"orm['logger.ExceptionMessage']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'logger.exceptiontraceback': {
            'Meta': {'object_name': 'ExceptionTraceback'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'exception_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'traceback'", 'to': u"orm['logger.ExceptionMessage']"}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'function_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line_num': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'logger.logmessage': {
            'Meta': {'ordering': "['-id', '-create_time']", 'object_name': 'LogMessage'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'logger_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'module_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        settings.AUTH_USER_MODEL: {
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
        }
    }

    complete_apps = ['logger']
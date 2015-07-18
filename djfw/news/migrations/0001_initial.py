# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'NewsItem'
        db.create_table('news_newsitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(default='', max_length=300)),
            ('announcement', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('full_text', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('is_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('published_at', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('news', ['NewsItem'])

    def backwards(self, orm):
        # Deleting model 'NewsItem'
        db.delete_table('news_newsitem')

    models = {
        'news.newsitem': {
            'Meta': {'ordering': "['position']", 'object_name': 'NewsItem'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['news']
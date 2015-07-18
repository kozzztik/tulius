# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SiteUpdate'
        db.create_table('bugs_siteupdate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('revision', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('bugs', ['SiteUpdate'])

        # Adding model 'SiteUpdateIssues'
        db.create_table('bugs_siteupdateissues', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('update', self.gf('django.db.models.fields.related.ForeignKey')(related_name='issues', to=orm['bugs.SiteUpdate'])),
            ('issue', self.gf('django.db.models.fields.related.ForeignKey')(related_name='site_updates', to=orm['bugtracker.Bug'])),
        ))
        db.send_create_signal('bugs', ['SiteUpdateIssues'])


    def backwards(self, orm):
        # Deleting model 'SiteUpdate'
        db.delete_table('bugs_siteupdate')

        # Deleting model 'SiteUpdateIssues'
        db.delete_table('bugs_siteupdateissues')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bugs.siteupdate': {
            'Meta': {'object_name': 'SiteUpdate'},
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'bugs.siteupdateissues': {
            'Meta': {'object_name': 'SiteUpdateIssues'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issue': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'site_updates'", 'to': "orm['bugtracker.Bug']"}),
            'update': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'issues'", 'to': "orm['bugs.SiteUpdate']"})
        },
        'bugtracker.bug': {
            'Meta': {'ordering': "['priority', '-create_time']", 'object_name': 'Bug'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_assigned'", 'null': 'True', 'to': "orm['bugtracker.JiraUser']"}),
            'bug_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': "orm['bugtracker.BugType']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'environment': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jira_reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_reported'", 'null': 'True', 'to': "orm['bugtracker.JiraUser']"}),
            'jira_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs'", 'null': 'True', 'to': "orm['bugtracker.BugPriority']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_reported'", 'null': 'True', 'to': "orm['auth.User']"}),
            'resolution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs'", 'null': 'True', 'to': "orm['bugtracker.BugResolution']"}),
            'resolution_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': "orm['bugtracker.BugStatus']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'bugtracker.bugpriority': {
            'Meta': {'object_name': 'BugPriority'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status_color': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'bugtracker.bugresolution': {
            'Meta': {'object_name': 'BugResolution'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'bugtracker.bugstatus': {
            'Meta': {'object_name': 'BugStatus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'bugtracker.bugtype': {
            'Meta': {'ordering': "['name']", 'object_name': 'BugType'},
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subtask': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'bugtracker.jirauser': {
            'Meta': {'object_name': 'JiraUser'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'big_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jiraid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'small_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jira_data'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['bugs']
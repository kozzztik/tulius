# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.add_column(u'bugtracker_jirauser', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, default=None, related_name='jira_data', to=orm['tulius.User']),
                      keep_default=False)
        db.add_column(u'bugtracker_bug', 'new_reporter',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, default=None,  related_name='bugs_reported', to=orm['tulius.User']),
                      keep_default=False)
        db.add_column(u'bugtracker_buguploadedfile', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='bug_files', to=orm['tulius.User']),
                      keep_default=False)
        db.add_column(u'bugtracker_issuecomment', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, null=True, default=None, related_name='comments_on_issues', to=orm['tulius.User']),
                      keep_default=False)

    def backwards(self, orm):
        db.delete_column(u'bugtracker_jirauser', 'new_user_id')
        db.delete_column(u'bugtracker_bug', 'new_reporter_id')
        db.delete_column(u'bugtracker_buguploadedfile', 'new_user_id')
        db.delete_column(u'bugtracker_issuecomment', 'new_user_id')

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'bugtracker.bug': {
            'Meta': {'ordering': "['priority', '-create_time']", 'object_name': 'Bug'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_assigned'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'bug_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': u"orm['bugtracker.BugType']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'environment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jira_reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_reported'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'jira_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'priority': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs'", 'null': 'True', 'to': u"orm['bugtracker.BugPriority']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs_reported'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'resolution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'bugs'", 'null': 'True', 'to': u"orm['bugtracker.BugResolution']"}),
            'resolution_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': u"orm['bugtracker.BugStatus']"}),
            'summary': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'bugtracker.bugcomponent': {
            'Meta': {'object_name': 'BugComponent'},
            'assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'components_assigned'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'assignee_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isAssigneeTypeValid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'lead': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'components_leaded'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'real_assignee': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'components_real_assigned'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'real_assignee_type': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'bugtracker.bugcomponentlink': {
            'Meta': {'object_name': 'BugComponentLink'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'components'", 'to': u"orm['bugtracker.Bug']"}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': u"orm['bugtracker.BugComponent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'bugtracker.bugexception': {
            'Meta': {'object_name': 'BugException'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'exceptions'", 'to': u"orm['bugtracker.Bug']"}),
            'exception_message_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'bugtracker.bugfixversion': {
            'Meta': {'unique_together': "(('bug', 'version'),)", 'object_name': 'BugFixVersion'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fix_versions'", 'to': u"orm['bugtracker.Bug']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs_fix'", 'to': u"orm['bugtracker.BugVersion']"})
        },
        u'bugtracker.buglink': {
            'Meta': {'object_name': 'BugLink'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inward': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'outward_links'", 'null': 'True', 'to': u"orm['bugtracker.Bug']"}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'link_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'links'", 'to': u"orm['bugtracker.BugLinkType']"}),
            'outward': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'inward_links'", 'null': 'True', 'to': u"orm['bugtracker.Bug']"})
        },
        u'bugtracker.buglinktype': {
            'Meta': {'object_name': 'BugLinkType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inward': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'outward': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'bugtracker.bugpriority': {
            'Meta': {'object_name': 'BugPriority'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status_color': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'bugtracker.bugresolution': {
            'Meta': {'object_name': 'BugResolution'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'bugtracker.bugstatus': {
            'Meta': {'object_name': 'BugStatus'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'bugtracker.bugsubtask': {
            'Meta': {'object_name': 'BugSubTask'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'subtask'", 'to': u"orm['bugtracker.Bug']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parent_bug'", 'to': u"orm['bugtracker.Bug']"})
        },
        u'bugtracker.bugtrackersetting': {
            'Meta': {'object_name': 'BugtrackerSetting'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'bugtracker.bugtype': {
            'Meta': {'ordering': "['name']", 'object_name': 'BugType'},
            'icon': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'subtask': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'bugtracker.buguploadedfile': {
            'Meta': {'object_name': 'BugUploadedFile'},
            'body': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'files'", 'null': 'True', 'to': u"orm['bugtracker.Bug']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bug_files'", 'to': u"orm['auth.User']"})
        },
        u'bugtracker.bugversion': {
            'Meta': {'ordering': "['-name']", 'object_name': 'BugVersion'},
            'archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0', 'unique': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'release_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'released': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'user_release_date': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'bugtracker.issueattachment': {
            'Meta': {'object_name': 'IssueAttachment'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['bugtracker.Bug']"}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'jira_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': u"orm['bugtracker.JiraUser']"}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'bugtracker.issuecomment': {
            'Meta': {'object_name': 'IssueComment'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['bugtracker.Bug']"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_updated_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'updated_comments'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'jira_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments'", 'null': 'True', 'to': u"orm['bugtracker.JiraUser']"}),
            'jiraid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'comments_on_issues'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'bugtracker.jirauser': {
            'Meta': {'object_name': 'JiraUser'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'big_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jira_url': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'jiraid': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'small_icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'jira_data'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'bugtracker.versionbug': {
            'Meta': {'object_name': 'VersionBug'},
            'bug': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'versions'", 'to': u"orm['bugtracker.Bug']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'version': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bugs'", 'to': u"orm['bugtracker.BugVersion']"})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'tulius.user': {
            'Meta': {'object_name': 'User'},
            'avatar': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'compact_text': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'hide_trustmarks': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'rank': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'show_online_status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_played_characters': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_played_games': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signature': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '400', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['bugtracker', 'tulius']
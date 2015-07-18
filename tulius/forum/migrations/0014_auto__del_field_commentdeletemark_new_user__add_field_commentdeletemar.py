# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.rename_column('forum_commentdeletemark', 'new_user_id', 'user_id')
        db.rename_column('forum_votingvote', 'new_user_id', 'user_id')

        db.create_unique(u'forum_votingvote', ['choice_id', 'user_id'])

        db.rename_column('forum_commentlike', 'new_user_id', 'user_id')
        db.rename_column('forum_threadreadmark', 'new_user_id', 'user_id')
        db.rename_column('forum_comment', 'new_user_id', 'user_id')
        db.rename_column('forum_comment', 'new_editor_id', 'editor_id')
        db.rename_column('forum_uploadedfile', 'new_user_id', 'user_id')
        db.rename_column('forum_threadcollapsestatus', 'new_user_id', 'user_id')

        db.create_unique(u'forum_threadcollapsestatus', ['thread_id', 'user_id'])

        db.rename_column('forum_voting', 'new_user_id', 'user_id')
        db.rename_column('forum_thread', 'new_user_id', 'user_id')
        db.rename_column('forum_threaddeletemark', 'new_user_id', 'user_id')
        db.rename_column('forum_threadaccessright', 'new_user_id', 'user_id')

        db.create_unique(u'forum_threadaccessright', ['thread_id', 'user_id'])

        db.rename_column('forum_onlineuser', 'new_user_id', 'user_id')

    def backwards(self, orm):
        db.rename_column('forum_onlineuser', 'user_id', 'new_user_id')

        # Removing unique constraint on 'ThreadAccessRight', fields ['thread', 'user']
        db.delete_unique(u'forum_threadaccessright', ['thread_id', 'user_id'])

        db.rename_column('forum_voting', 'user_id', 'new_user_id')
        db.rename_column('forum_thread', 'user_id', 'new_user_id')
        db.rename_column('forum_threaddeletemark', 'user_id', 'new_user_id')
        db.rename_column('forum_threadaccessright', 'user_id', 'new_user_id')

        # Removing unique constraint on 'ThreadCollapseStatus', fields ['thread', 'user']
        db.delete_unique(u'forum_threadcollapsestatus', ['thread_id', 'user_id'])

        db.rename_column('forum_commentlike', 'user_id', 'new_user_id')
        db.rename_column('forum_threadreadmark', 'user_id', 'new_user_id')
        db.rename_column('forum_comment', 'user_id', 'new_user_id')
        db.rename_column('forum_comment', 'editor_id', 'new_editor_id')
        db.rename_column('forum_uploadedfile', 'user_id', 'new_user_id')
        db.rename_column('forum_threadcollapsestatus', 'user_id', 'new_user_id')

        # Removing unique constraint on 'VotingVote', fields ['choice', 'user']
        db.delete_unique(u'forum_votingvote', ['choice_id', 'user_id'])

        db.rename_column('forum_commentdeletemark', 'user_id', 'new_user_id')
        db.rename_column('forum_votingvote', 'user_id', 'new_user_id')

    models = {
        u'forum.comment': {
            'Meta': {'ordering': "['id']", 'object_name': 'Comment'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'edit_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'forum_comments_edited'", 'null': 'True', 'to': u"orm['tulius.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'comments'", 'to': u"orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answers'", 'null': 'True', 'to': u"orm['forum.Comment']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_comments'", 'to': u"orm['tulius.User']"}),
            'voting': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'forum.commentdeletemark': {
            'Meta': {'object_name': 'CommentDeleteMark'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delete_marks'", 'to': u"orm['forum.Comment']"}),
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments_delete_marks'", 'to': u"orm['tulius.User']"})
        },
        u'forum.commentlike': {
            'Meta': {'object_name': 'CommentLike'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'liked'", 'to': u"orm['forum.Comment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'liked_comments'", 'to': u"orm['tulius.User']"})
        },
        u'forum.onlineuser': {
            'Meta': {'object_name': 'OnlineUser'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'visit_marks'", 'to': u"orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_visit'", 'to': u"orm['tulius.User']"}),
            'visit_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'forum.thread': {
            'Meta': {'ordering': "['-important', 'id']", 'object_name': 'Thread'},
            'access_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_comment_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_comment_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'protected_threads': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': u"orm['tulius.User']"})
        },
        u'forum.threadaccessright': {
            'Meta': {'unique_together': "(('thread', 'user'),)", 'object_name': 'ThreadAccessRight'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rights'", 'to': u"orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_theads_rights'", 'to': u"orm['tulius.User']"})
        },
        u'forum.threadcollapsestatus': {
            'Meta': {'unique_together': "(('thread', 'user'),)", 'object_name': 'ThreadCollapseStatus'},
            'collapse_rooms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'collapse_threads': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['tulius.User']"})
        },
        u'forum.threaddeletemark': {
            'Meta': {'object_name': 'ThreadDeleteMark'},
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delete_marks'", 'to': u"orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thread_delete_marks'", 'to': u"orm['tulius.User']"})
        },
        u'forum.threadreadmark': {
            'Meta': {'object_name': 'ThreadReadMark'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'not_readed_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'not_readed_users'", 'null': 'True', 'to': u"orm['forum.Comment']"}),
            'readed_comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readed_users'", 'to': u"orm['forum.Comment']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'read_marks'", 'to': u"orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_readed_threads'", 'to': u"orm['tulius.User']"})
        },
        u'forum.uploadedfile': {
            'Meta': {'object_name': 'UploadedFile'},
            'body': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_length': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_files'", 'to': u"orm['tulius.User']"})
        },
        u'forum.voting': {
            'Meta': {'object_name': 'Voting'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_list'", 'to': u"orm['forum.Comment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_results': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'create_votings'", 'to': u"orm['tulius.User']"}),
            'voting_body': ('django.db.models.fields.TextField', [], {}),
            'voting_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        u'forum.votingchoice': {
            'Meta': {'object_name': 'VotingChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'voting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': u"orm['forum.Voting']"})
        },
        u'forum.votingvote': {
            'Meta': {'unique_together': "(('choice', 'user'),)", 'object_name': 'VotingVote'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_choices'", 'to': u"orm['forum.VotingChoice']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_votes'", 'to': u"orm['tulius.User']"})
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

    complete_apps = ['forum']
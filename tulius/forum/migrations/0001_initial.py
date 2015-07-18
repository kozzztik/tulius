# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'RoomGroup'
        db.create_table('forum_roomgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('forum', ['RoomGroup'])

        # Adding model 'UploadedFile'
        db.create_table('forum_uploadedfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_files', to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('mime', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('body', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('file_length', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('forum', ['UploadedFile'])

        # Adding model 'Thread'
        db.create_table('forum_thread', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name='children', null=True, to=orm['forum.Thread'])),
            ('room', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_threads', to=orm['auth.User'])),
            ('plugin_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('access_type', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('important', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('protected_threads', self.gf('django.db.models.fields.SmallIntegerField')(default=False)),
            ('first_comment', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_comment', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('comments_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_num', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('data1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('data2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('forum', ['Thread'])

        # Adding model 'ThreadAccessRight'
        db.create_table('forum_threadaccessright', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rights', to=orm['forum.Thread'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_theads_rights', to=orm['auth.User'])),
            ('access_level', self.gf('django.db.models.fields.SmallIntegerField')(default=0)),
        ))
        db.send_create_signal('forum', ['ThreadAccessRight'])

        # Adding unique constraint on 'ThreadAccessRight', fields ['thread', 'user']
        db.create_unique('forum_threadaccessright', ['thread_id', 'user_id'])

        # Adding model 'Comment'
        db.create_table('forum_comment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(related_name='comments', to=orm['forum.Thread'])),
            ('plugin_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_comments', to=orm['auth.User'])),
            ('editor', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='forum_comments_edited', null=True, to=orm['auth.User'])),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('edit_time', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('reply', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='answers', null=True, to=orm['forum.Comment'])),
            ('voting', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('likes', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('num', self.gf('django.db.models.fields.IntegerField')()),
            ('data1', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('data2', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('forum', ['Comment'])

        # Adding model 'ThreadReadMark'
        db.create_table('forum_threadreadmark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='read_marks', to=orm['forum.Thread'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_readed_threads', to=orm['auth.User'])),
            ('readed_comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='readed_users', to=orm['forum.Comment'])),
            ('not_readed_comment', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='not_readed_users', null=True, to=orm['forum.Comment'])),
        ))
        db.send_create_signal('forum', ['ThreadReadMark'])

        # Adding model 'ThreadGroupLink'
        db.create_table('forum_threadgrouplink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='room_group', to=orm['forum.Thread'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='threads', null=True, to=orm['forum.RoomGroup'])),
        ))
        db.send_create_signal('forum', ['ThreadGroupLink'])

        # Adding model 'CommentLike'
        db.create_table('forum_commentlike', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='liked_comments', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='liked', to=orm['forum.Comment'])),
        ))
        db.send_create_signal('forum', ['CommentLike'])

        # Adding model 'ThreadDeleteMark'
        db.create_table('forum_threaddeletemark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='delete_marks', to=orm['forum.Thread'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thread_delete_marks', to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('forum', ['ThreadDeleteMark'])

        # Adding model 'CommentDeleteMark'
        db.create_table('forum_commentdeletemark', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='delete_marks', to=orm['forum.Comment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments_delete_marks', to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('deleted', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('delete_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('forum', ['CommentDeleteMark'])

        # Adding model 'OnlineUser'
        db.create_table('forum_onlineuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forum_visit', to=orm['auth.User'])),
            ('visit_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(related_name='visit_marks', to=orm['forum.Thread'])),
        ))
        db.send_create_signal('forum', ['OnlineUser'])

        # Adding model 'Voting'
        db.create_table('forum_voting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='create_votings', to=orm['auth.User'])),
            ('comment', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voting_list', to=orm['forum.Comment'])),
            ('voting_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('voting_body', self.gf('django.db.models.fields.TextField')()),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('anonymous', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_results', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('preview_results', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('forum', ['Voting'])

        # Adding model 'VotingChoice'
        db.create_table('forum_votingchoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('voting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='choices', to=orm['forum.Voting'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
        ))
        db.send_create_signal('forum', ['VotingChoice'])

        # Adding model 'VotingVote'
        db.create_table('forum_votingvote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('choice', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voting_choices', to=orm['forum.VotingChoice'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='voting_votes', to=orm['auth.User'])),
        ))
        db.send_create_signal('forum', ['VotingVote'])

        # Adding unique constraint on 'VotingVote', fields ['choice', 'user']
        db.create_unique('forum_votingvote', ['choice_id', 'user_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'VotingVote', fields ['choice', 'user']
        db.delete_unique('forum_votingvote', ['choice_id', 'user_id'])

        # Removing unique constraint on 'ThreadAccessRight', fields ['thread', 'user']
        db.delete_unique('forum_threadaccessright', ['thread_id', 'user_id'])

        # Deleting model 'RoomGroup'
        db.delete_table('forum_roomgroup')

        # Deleting model 'UploadedFile'
        db.delete_table('forum_uploadedfile')

        # Deleting model 'Thread'
        db.delete_table('forum_thread')

        # Deleting model 'ThreadAccessRight'
        db.delete_table('forum_threadaccessright')

        # Deleting model 'Comment'
        db.delete_table('forum_comment')

        # Deleting model 'ThreadReadMark'
        db.delete_table('forum_threadreadmark')

        # Deleting model 'ThreadGroupLink'
        db.delete_table('forum_threadgrouplink')

        # Deleting model 'CommentLike'
        db.delete_table('forum_commentlike')

        # Deleting model 'ThreadDeleteMark'
        db.delete_table('forum_threaddeletemark')

        # Deleting model 'CommentDeleteMark'
        db.delete_table('forum_commentdeletemark')

        # Deleting model 'OnlineUser'
        db.delete_table('forum_onlineuser')

        # Deleting model 'Voting'
        db.delete_table('forum_voting')

        # Deleting model 'VotingChoice'
        db.delete_table('forum_votingchoice')

        # Deleting model 'VotingVote'
        db.delete_table('forum_votingvote')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'forum.comment': {
            'Meta': {'ordering': "['id']", 'object_name': 'Comment'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'edit_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'forum_comments_edited'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'num': ('django.db.models.fields.IntegerField', [], {}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'related_name': "'comments'", 'to': "orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'reply': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answers'", 'null': 'True', 'to': "orm['forum.Comment']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_comments'", 'to': "orm['auth.User']"}),
            'voting': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'forum.commentdeletemark': {
            'Meta': {'object_name': 'CommentDeleteMark'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delete_marks'", 'to': "orm['forum.Comment']"}),
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments_delete_marks'", 'to': "orm['auth.User']"})
        },
        'forum.commentlike': {
            'Meta': {'object_name': 'CommentLike'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'liked'", 'to': "orm['forum.Comment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'liked_comments'", 'to': "orm['auth.User']"})
        },
        'forum.onlineuser': {
            'Meta': {'object_name': 'OnlineUser'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'visit_marks'", 'to': "orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_visit'", 'to': "orm['auth.User']"}),
            'visit_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'forum.roomgroup': {
            'Meta': {'object_name': 'RoomGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'forum.thread': {
            'Meta': {'ordering': "['-important', 'id']", 'object_name': 'Thread'},
            'access_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'body': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comments_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data1': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'data2': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'first_comment': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_comment': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'max_num': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'protected_threads': ('django.db.models.fields.SmallIntegerField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': "orm['auth.User']"})
        },
        'forum.threadaccessright': {
            'Meta': {'unique_together': "(('thread', 'user'),)", 'object_name': 'ThreadAccessRight'},
            'access_level': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rights'", 'to': "orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_theads_rights'", 'to': "orm['auth.User']"})
        },
        'forum.threaddeletemark': {
            'Meta': {'object_name': 'ThreadDeleteMark'},
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delete_marks'", 'to': "orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thread_delete_marks'", 'to': "orm['auth.User']"})
        },
        'forum.threadgrouplink': {
            'Meta': {'object_name': 'ThreadGroupLink'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'threads'", 'null': 'True', 'to': "orm['forum.RoomGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'room_group'", 'to': "orm['forum.Thread']"})
        },
        'forum.threadreadmark': {
            'Meta': {'object_name': 'ThreadReadMark'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'not_readed_comment': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'not_readed_users'", 'null': 'True', 'to': "orm['forum.Comment']"}),
            'readed_comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readed_users'", 'to': "orm['forum.Comment']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'read_marks'", 'to': "orm['forum.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_readed_threads'", 'to': "orm['auth.User']"})
        },
        'forum.uploadedfile': {
            'Meta': {'object_name': 'UploadedFile'},
            'body': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'file_length': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_files'", 'to': "orm['auth.User']"})
        },
        'forum.voting': {
            'Meta': {'object_name': 'Voting'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_list'", 'to': "orm['forum.Comment']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview_results': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_results': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'create_votings'", 'to': "orm['auth.User']"}),
            'voting_body': ('django.db.models.fields.TextField', [], {}),
            'voting_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'})
        },
        'forum.votingchoice': {
            'Meta': {'object_name': 'VotingChoice'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'voting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'choices'", 'to': "orm['forum.Voting']"})
        },
        'forum.votingvote': {
            'Meta': {'unique_together': "(('choice', 'user'),)", 'object_name': 'VotingVote'},
            'choice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_choices'", 'to': "orm['forum.VotingChoice']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'voting_votes'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['forum']
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'GameGuest.new_user'
        db.add_column(u'games_gameguest', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='guested_games', to=orm['tulius.User']),
                      keep_default=False)

        # Adding field 'GameInvite.new_user'
        db.add_column(u'games_gameinvite', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='invites', to=orm['tulius.User']),
                      keep_default=False)

        # Adding field 'GameInvite.new_sender'
        db.add_column(u'games_gameinvite', 'new_sender',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='sended_invites', to=orm['tulius.User']),
                      keep_default=False)

        # Adding field 'GameWinner.new_user'
        db.add_column(u'games_gamewinner', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='winned_games', to=orm['tulius.User']),
                      keep_default=False)

        # Adding field 'GameAdmin.new_user'
        db.add_column(u'games_gameadmin', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='admined_games', to=orm['tulius.User']),
                      keep_default=False)

        # Adding field 'RoleRequest.new_user'
        db.add_column(u'games_rolerequest', 'new_user',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='requested_games', to=orm['tulius.User']),
                      keep_default=False)


    def backwards(self, orm):

        # Deleting field 'GameGuest.new_user'
        db.delete_column(u'games_gameguest', 'new_user_id')

        # Deleting field 'GameInvite.new_user'
        db.delete_column(u'games_gameinvite', 'new_user_id')

        # Deleting field 'GameInvite.new_sender'
        db.delete_column(u'games_gameinvite', 'new_sender_id')

        # Deleting field 'GameWinner.new_user'
        db.delete_column(u'games_gamewinner', 'new_user_id')

        # Deleting field 'GameAdmin.new_user'
        db.delete_column(u'games_gameadmin', 'new_user_id')

        # Deleting field 'RoleRequest.new_user'
        db.delete_column(u'games_rolerequest', 'new_user_id')


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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': u"orm['auth.User']"})
        },
        u'games.game': {
            'Meta': {'object_name': 'Game'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'announcement_preview': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'bottom_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'card_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'requests_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'serial_number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'short_comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'show_announcement': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'games'", 'null': 'True', 'to': u"orm['games.Skin']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'top_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games'", 'to': u"orm['stories.Variation']"})
        },
        u'games.gameadmin': {
            'Meta': {'unique_together': "(('game', 'new_user'),)", 'object_name': 'GameAdmin'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admins'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admined_games'", 'to': u"orm['tulius.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admined_games'", 'to': u"orm['auth.User']"})
        },
        u'games.gameguest': {
            'Meta': {'unique_together': "(('game', 'new_user'),)", 'object_name': 'GameGuest'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guests'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guested_games'", 'to': u"orm['tulius.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guested_games'", 'to': u"orm['auth.User']"})
        },
        u'games.gameinvite': {
            'Meta': {'ordering': "['-id']", 'object_name': 'GameInvite'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sended_invites'", 'to': u"orm['tulius.User']"}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': u"orm['tulius.User']"}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': u"orm['stories.Role']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sended_invites'", 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': u"orm['auth.User']"})
        },
        u'games.gamewinner': {
            'Meta': {'unique_together': "(('game', 'new_user'),)", 'object_name': 'GameWinner'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winners'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winned_games'", 'to': u"orm['tulius.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winned_games'", 'to': u"orm['auth.User']"})
        },
        u'games.requestquestion': {
            'Meta': {'object_name': 'RequestQuestion'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'request_questions'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'})
        },
        u'games.requestquestionanswer': {
            'Meta': {'object_name': 'RequestQuestionAnswer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['games.RequestQuestion']"}),
            'role_request': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': u"orm['games.RoleRequest']"})
        },
        u'games.rolerequest': {
            'Meta': {'object_name': 'RoleRequest'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_requests'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_games'", 'to': u"orm['tulius.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_games'", 'to': u"orm['auth.User']"})
        },
        u'games.rolerequestselection': {
            'Meta': {'unique_together': "(('role_request', 'role'),)", 'object_name': 'RoleRequestSelection'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefer_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requests'", 'to': u"orm['stories.Role']"}),
            'role_request': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'selections'", 'to': u"orm['games.RoleRequest']"})
        },
        u'games.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'stories.avatar': {
            'Meta': {'object_name': 'Avatar'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'avatars'", 'to': u"orm['stories.Story']"})
        },
        u'stories.character': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Character'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': u"orm['stories.Avatar']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'characters'", 'to': u"orm['stories.Story']"})
        },
        u'stories.genre': {
            'Meta': {'object_name': 'Genre'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'stories.role': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Role'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': u"orm['stories.Avatar']"}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'character': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': u"orm['stories.Character']"}),
            'comments_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'requestable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_online_character': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_trust_marks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'trust_value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': u"orm['tulius.User']"}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['stories.Variation']"}),
            'visit_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'stories.story': {
            'Meta': {'object_name': 'Story'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'announcement_preview': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'bottom_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'card_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'creation_year': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'stories'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['stories.Genre']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'short_comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'top_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        u'stories.variation': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Variation'},
            'comments_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'story_variation'", 'null': 'True', 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variations'", 'to': u"orm['stories.Story']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variations'", 'null': 'True', 'to': u"orm['forum.Thread']"})
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

    complete_apps = ['games']
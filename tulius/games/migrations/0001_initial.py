# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Skin'
        db.create_table('games_skin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('games', ['Skin'])

        # Adding model 'Game'
        db.create_table('games_game', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('variation', self.gf('django.db.models.fields.related.ForeignKey')(related_name='games', to=orm['stories.Variation'])),
            ('serial_number', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=200)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('announcement', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('announcement_preview', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('short_comment', self.gf('django.db.models.fields.CharField')(default='', max_length=500, blank=True)),
            ('introduction', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('requests_text', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('card_image', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('top_banner', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('bottom_banner', self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True)),
            ('show_announcement', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('skin', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='games', null=True, to=orm['games.Skin'])),
        ))
        db.send_create_signal('games', ['Game'])

        # Adding model 'GameAdmin'
        db.create_table('games_gameadmin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admins', to=orm['games.Game'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='admined_games', to=orm['auth.User'])),
        ))
        db.send_create_signal('games', ['GameAdmin'])

        # Adding unique constraint on 'GameAdmin', fields ['game', 'user']
        db.create_unique('games_gameadmin', ['game_id', 'user_id'])

        # Adding model 'GameGuest'
        db.create_table('games_gameguest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='guests', to=orm['games.Game'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='guested_games', to=orm['auth.User'])),
        ))
        db.send_create_signal('games', ['GameGuest'])

        # Adding unique constraint on 'GameGuest', fields ['game', 'user']
        db.create_unique('games_gameguest', ['game_id', 'user_id'])

        # Adding model 'GameWinner'
        db.create_table('games_gamewinner', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='winners', to=orm['games.Game'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='winned_games', to=orm['auth.User'])),
        ))
        db.send_create_signal('games', ['GameWinner'])

        # Adding unique constraint on 'GameWinner', fields ['game', 'user']
        db.create_unique('games_gamewinner', ['game_id', 'user_id'])

        # Adding model 'RoleRequest'
        db.create_table('games_rolerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='role_requests', to=orm['games.Game'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requested_games', to=orm['auth.User'])),
            ('body', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('games', ['RoleRequest'])

        # Adding model 'RoleRequestSelection'
        db.create_table('games_rolerequestselection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role_request', self.gf('django.db.models.fields.related.ForeignKey')(related_name='selections', to=orm['games.RoleRequest'])),
            ('prefer_order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='requests', to=orm['stories.Role'])),
        ))
        db.send_create_signal('games', ['RoleRequestSelection'])

        # Adding unique constraint on 'RoleRequestSelection', fields ['role_request', 'role']
        db.create_unique('games_rolerequestselection', ['role_request_id', 'role_id'])

        # Adding model 'RequestQuestion'
        db.create_table('games_requestquestion', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('game', self.gf('django.db.models.fields.related.ForeignKey')(related_name='request_questions', to=orm['games.Game'])),
            ('question', self.gf('django.db.models.fields.CharField')(default='', max_length=500)),
        ))
        db.send_create_signal('games', ['RequestQuestion'])

        # Adding model 'RequestQuestionAnswer'
        db.create_table('games_requestquestionanswer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role_request', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['games.RoleRequest'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name='answers', to=orm['games.RequestQuestion'])),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=500)),
        ))
        db.send_create_signal('games', ['RequestQuestionAnswer'])

        # Adding model 'GameInvite'
        db.create_table('games_gameinvite', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('role', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invites', to=orm['stories.Role'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invites', to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sended_invites', to=orm['auth.User'])),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('games', ['GameInvite'])


    def backwards(self, orm):
        # Removing unique constraint on 'RoleRequestSelection', fields ['role_request', 'role']
        db.delete_unique('games_rolerequestselection', ['role_request_id', 'role_id'])

        # Removing unique constraint on 'GameWinner', fields ['game', 'user']
        db.delete_unique('games_gamewinner', ['game_id', 'user_id'])

        # Removing unique constraint on 'GameGuest', fields ['game', 'user']
        db.delete_unique('games_gameguest', ['game_id', 'user_id'])

        # Removing unique constraint on 'GameAdmin', fields ['game', 'user']
        db.delete_unique('games_gameadmin', ['game_id', 'user_id'])

        # Deleting model 'Skin'
        db.delete_table('games_skin')

        # Deleting model 'Game'
        db.delete_table('games_game')

        # Deleting model 'GameAdmin'
        db.delete_table('games_gameadmin')

        # Deleting model 'GameGuest'
        db.delete_table('games_gameguest')

        # Deleting model 'GameWinner'
        db.delete_table('games_gamewinner')

        # Deleting model 'RoleRequest'
        db.delete_table('games_rolerequest')

        # Deleting model 'RoleRequestSelection'
        db.delete_table('games_rolerequestselection')

        # Deleting model 'RequestQuestion'
        db.delete_table('games_requestquestion')

        # Deleting model 'RequestQuestionAnswer'
        db.delete_table('games_requestquestionanswer')

        # Deleting model 'GameInvite'
        db.delete_table('games_gameinvite')


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
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'protected_threads': ('django.db.models.fields.SmallIntegerField', [], {'default': 'False'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': "orm['auth.User']"})
        },
        'games.game': {
            'Meta': {'object_name': 'Game'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'announcement_preview': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'bottom_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'card_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'requests_text': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'serial_number': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'short_comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'show_announcement': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'skin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'games'", 'null': 'True', 'to': "orm['games.Skin']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'top_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games'", 'to': "orm['stories.Variation']"})
        },
        'games.gameadmin': {
            'Meta': {'unique_together': "(('game', 'user'),)", 'object_name': 'GameAdmin'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admins'", 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admined_games'", 'to': "orm['auth.User']"})
        },
        'games.gameguest': {
            'Meta': {'unique_together': "(('game', 'user'),)", 'object_name': 'GameGuest'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guests'", 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guested_games'", 'to': "orm['auth.User']"})
        },
        'games.gameinvite': {
            'Meta': {'ordering': "['-id']", 'object_name': 'GameInvite'},
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': "orm['stories.Role']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sended_invites'", 'to': "orm['auth.User']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invites'", 'to': "orm['auth.User']"})
        },
        'games.gamewinner': {
            'Meta': {'unique_together': "(('game', 'user'),)", 'object_name': 'GameWinner'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winners'", 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winned_games'", 'to': "orm['auth.User']"})
        },
        'games.requestquestion': {
            'Meta': {'object_name': 'RequestQuestion'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'request_questions'", 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'})
        },
        'games.requestquestionanswer': {
            'Meta': {'object_name': 'RequestQuestionAnswer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['games.RequestQuestion']"}),
            'role_request': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'answers'", 'to': "orm['games.RoleRequest']"})
        },
        'games.rolerequest': {
            'Meta': {'object_name': 'RoleRequest'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_requests'", 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requested_games'", 'to': "orm['auth.User']"})
        },
        'games.rolerequestselection': {
            'Meta': {'unique_together': "(('role_request', 'role'),)", 'object_name': 'RoleRequestSelection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefer_order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'requests'", 'to': "orm['stories.Role']"}),
            'role_request': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'selections'", 'to': "orm['games.RoleRequest']"})
        },
        'games.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'stories.avatar': {
            'Meta': {'object_name': 'Avatar'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'avatars'", 'to': "orm['stories.Story']"})
        },
        'stories.character': {
            'Meta': {'object_name': 'Character'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': "orm['stories.Avatar']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'characters'", 'to': "orm['stories.Story']"})
        },
        'stories.genre': {
            'Meta': {'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'stories.role': {
            'Meta': {'object_name': 'Role'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': "orm['stories.Avatar']"}),
            'body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'character': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': "orm['stories.Character']"}),
            'comments_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'requestable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_online_character': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_trust_marks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'trust_value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': "orm['auth.User']"}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['stories.Variation']"}),
            'visit_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'stories.story': {
            'Meta': {'object_name': 'Story'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'announcement_preview': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'bottom_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'card_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'creation_year': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'genres': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'stories'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['stories.Genre']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'short_comment': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'top_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'stories.variation': {
            'Meta': {'object_name': 'Variation'},
            'comments_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'story_variation'", 'null': 'True', 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variations'", 'to': "orm['stories.Story']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variations'", 'null': 'True', 'to': "orm['forum.Thread']"})
        }
    }

    complete_apps = ['games']
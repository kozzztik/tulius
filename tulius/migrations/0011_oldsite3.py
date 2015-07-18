# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        db.delete_column(u'old_site_migrate_olduser', 'user_id')
        db.rename_column('old_site_migrate_olduser', 'new_user_id', 'user_id')

    def backwards(self, orm):
        db.rename_column('old_site_migrate_olduser', 'user_id', 'new_user_id')
        db.add_column(u'old_site_migrate_olduser', 'user_id',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='old_version', to=orm['auth.User']),
                      keep_default=False)

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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': u"orm['tulius.User']"})
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
            'Meta': {'unique_together': "(('game', 'user'),)", 'object_name': 'GameAdmin'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admins'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admined_games'", 'to': u"orm['tulius.User']"})
        },
        u'games.gameguest': {
            'Meta': {'unique_together': "(('game', 'user'),)", 'object_name': 'GameGuest'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guests'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guested_games'", 'to': u"orm['tulius.User']"})
        },
        u'games.gamewinner': {
            'Meta': {'object_name': 'GameWinner'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winners'", 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winned_games'", 'to': u"orm['tulius.User']"})
        },
        u'games.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'news.newsitem': {
            'Meta': {'ordering': "['-published_at']", 'object_name': 'NewsItem'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'old_site_migrate.oldgame': {
            'Meta': {'object_name': 'OldGame'},
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['games.Game']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'synced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'old_site_migrate.oldgameadmin': {
            'Meta': {'object_name': 'OldGameAdmin'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['games.GameAdmin']"}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admins'", 'to': u"orm['old_site_migrate.OldGame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games_admined'", 'to': u"orm['old_site_migrate.OldUser']"})
        },
        u'old_site_migrate.oldgameguest': {
            'Meta': {'object_name': 'OldGameGuest'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'guests'", 'to': u"orm['old_site_migrate.OldGame']"}),
            'guest': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['games.GameGuest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games_guested'", 'to': u"orm['old_site_migrate.OldUser']"})
        },
        u'old_site_migrate.oldgamewinner': {
            'Meta': {'object_name': 'OldGameWinner'},
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'winners'", 'to': u"orm['old_site_migrate.OldGame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'games_winned'", 'to': u"orm['old_site_migrate.OldUser']"}),
            'winner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['games.GameWinner']"})
        },
        u'old_site_migrate.oldillustration': {
            'Meta': {'object_name': 'OldIllustration'},
            'bottom_banner': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ext': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'illustrations'", 'to': u"orm['old_site_migrate.OldGame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'illustration': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['stories.Illustration']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'param1': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'param2': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'top_banner': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'old_site_migrate.oldnews': {
            'Meta': {'object_name': 'OldNews'},
            'body': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'news_item': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_versions'", 'null': 'True', 'to': u"orm['news.NewsItem']"}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        u'old_site_migrate.oldrole': {
            'Meta': {'object_name': 'OldRole'},
            'comment': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': u"orm['old_site_migrate.OldGame']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'requestable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['stories.Role']"}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_trust': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': u"orm['old_site_migrate.OldUser']"})
        },
        u'old_site_migrate.oldsmile': {
            'Meta': {'object_name': 'OldSmile'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'old_site_migrate.olduser': {
            'Meta': {'object_name': 'OldUser'},
            'aol': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'convert_smiles': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hide_on_forum': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hide_trust': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hobby': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'html': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'icq': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'last_visited': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'msn': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'new_user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['tulius.User']"}),
            'notify_by_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'old_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'profession': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'rank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'show_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_subpost': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'smiles': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subpost': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'old_version'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'yahoo': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        u'stories.illustration': {
            'Meta': {'object_name': 'Illustration'},
            'admins_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'illustrations'", 'null': 'True', 'to': u"orm['stories.Story']"}),
            'thumb': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'illustrations'", 'null': 'True', 'to': u"orm['stories.Variation']"})
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

    complete_apps = ['old_site_migrate', 'tulius']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Role.order'
        db.add_column('stories_role', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Role.order'
        db.delete_column('stories_role', 'order')


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
            'first_comment_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'important': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_comment_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['forum.Thread']"}),
            'plugin_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'protected_threads': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forum_threads'", 'to': "orm['auth.User']"})
        },
        'games.game': {
            'Meta': {'object_name': 'Game'},
            'announcement': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'announcement_preview': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'bottom_banner': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'card_image': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
        'games.skin': {
            'Meta': {'object_name': 'Skin'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'stories.additionalmaterial': {
            'Meta': {'object_name': 'AdditionalMaterial'},
            'admins_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'additional_materials'", 'null': 'True', 'to': "orm['stories.Story']"}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'additional_materials'", 'null': 'True', 'to': "orm['stories.Variation']"})
        },
        'stories.avatar': {
            'Meta': {'object_name': 'Avatar'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'avatars'", 'to': "orm['stories.Story']"})
        },
        'stories.avataralternative': {
            'Meta': {'object_name': 'AvatarAlternative'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'alternatives'", 'to': "orm['stories.Avatar']"}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'stories.character': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Character'},
            'avatar': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'characters'", 'null': 'True', 'to': "orm['stories.Avatar']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'characters'", 'to': "orm['stories.Story']"})
        },
        'stories.genre': {
            'Meta': {'object_name': 'Genre'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'})
        },
        'stories.illustration': {
            'Meta': {'object_name': 'Illustration'},
            'admins_only': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'illustrations'", 'null': 'True', 'to': "orm['stories.Story']"}),
            'thumb': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'illustrations'", 'null': 'True', 'to': "orm['stories.Variation']"})
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
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'requestable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_in_character_list': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_in_online_character': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_trust_marks': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'trust_value': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'roles'", 'null': 'True', 'to': "orm['auth.User']"}),
            'variation': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'roles'", 'to': "orm['stories.Variation']"}),
            'visit_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'stories.roledeletemark': {
            'Meta': {'object_name': 'RoleDeleteMark'},
            'delete_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delete_marks'", 'to': "orm['stories.Role']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'role_delete_marks'", 'to': "orm['auth.User']"})
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
        'stories.storyadmin': {
            'Meta': {'unique_together': "(('story', 'user'),)", 'object_name': 'StoryAdmin'},
            'create_game': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admins'", 'to': "orm['stories.Story']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admined stories'", 'to': "orm['auth.User']"})
        },
        'stories.storyauthor': {
            'Meta': {'unique_together': "(('story', 'user'),)", 'object_name': 'StoryAuthor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authors'", 'to': "orm['stories.Story']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authored_stories'", 'to': "orm['auth.User']"})
        },
        'stories.variation': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Variation'},
            'comments_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'game': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'story_variation'", 'null': 'True', 'to': "orm['games.Game']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'story': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'variations'", 'to': "orm['stories.Story']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'variations'", 'null': 'True', 'to': "orm['forum.Thread']"})
        }
    }

    complete_apps = ['stories']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Submittal'
        db.create_table('portal_submittal', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('media_title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('media_description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('media_channel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['portal.Channel'], null=True, blank=True)),
            ('media_license', self.gf('django.db.models.fields.CharField')(default='CC-BY', max_length=200)),
            ('media_linkURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_kind', self.gf('django.db.models.fields.IntegerField')(max_length=1)),
            ('media_torrentURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_mp4URL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_webmURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_mp3URL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_oggURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_videoThumbURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_audioThumbURL', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('media_published', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('media_torrentDone', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('portal', ['Submittal'])

        # Adding M2M table for field users on 'Submittal'
        db.create_table('portal_submittal_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('submittal', models.ForeignKey(orm['portal.submittal'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('portal_submittal_users', ['submittal_id', 'user_id'])


    def backwards(self, orm):
        # Deleting model 'Submittal'
        db.delete_table('portal_submittal')

        # Removing M2M table for field users on 'Submittal'
        db.delete_table('portal_submittal_users')


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
        'portal.channel': {
            'Meta': {'object_name': 'Channel'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'})
        },
        'portal.collection': {
            'Meta': {'object_name': 'Collection'},
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.Channel']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'videos': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['portal.Video']", 'symmetrical': 'False'})
        },
        'portal.comment': {
            'Meta': {'object_name': 'Comment'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'moderated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'timecode': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.Video']"})
        },
        'portal.hotfolder': {
            'Meta': {'object_name': 'Hotfolder'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'autoPublish': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.Channel']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'defaultName': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'folderName': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'portal.submittal': {
            'Meta': {'object_name': 'Submittal'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'media_audioThumbURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.Channel']", 'null': 'True', 'blank': 'True'}),
            'media_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'media_kind': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'media_license': ('django.db.models.fields.CharField', [], {'default': "'CC-BY'", 'max_length': '200'}),
            'media_linkURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_mp3URL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_mp4URL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_oggURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'media_torrentDone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'media_torrentURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_videoThumbURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'media_webmURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'portal.video': {
            'Meta': {'object_name': 'Video'},
            'assemblyid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'audioThumbURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'autoPublish': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'channel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['portal.Channel']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'encodingDone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.IntegerField', [], {'max_length': '1'}),
            'license': ('django.db.models.fields.CharField', [], {'default': "'CC-BY'", 'max_length': '200'}),
            'linkURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'mp3Size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp3URL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'mp4Size': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mp4URL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'oggSize': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'oggURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'originalFile': ('django.db.models.fields.files.FileField', [], {'max_length': '2048'}),
            'published': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'torrentDone': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'torrentURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'videoThumbURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'webmSize': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'webmURL': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_tagged_items'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['portal']
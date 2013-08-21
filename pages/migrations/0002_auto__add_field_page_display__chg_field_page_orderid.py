# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Page.display'
        db.add_column('pages_page', 'display',
                      self.gf('django.db.models.fields.CharField')(default='body', max_length=20),
                      keep_default=False)


        # Changing field 'Page.orderid'
        db.alter_column('pages_page', 'orderid', self.gf('django.db.models.fields.DecimalField')(unique=True, max_digits=2, decimal_places=2))

    def backwards(self, orm):
        # Deleting field 'Page.display'
        db.delete_column('pages_page', 'display')


        # Changing field 'Page.orderid'
        db.alter_column('pages_page', 'orderid', self.gf('django.db.models.fields.DecimalField')(unique=True, max_digits=10, decimal_places=2))

    models = {
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {'max_length': '10000', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display': ('django.db.models.fields.CharField', [], {'default': "'body'", 'max_length': '20'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'orderid': ('django.db.models.fields.DecimalField', [], {'unique': 'True', 'max_digits': '2', 'decimal_places': '2'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['pages']
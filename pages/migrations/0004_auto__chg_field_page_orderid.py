# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Page.orderid'
        db.alter_column('pages_page', 'orderid', self.gf('django.db.models.fields.DecimalField')(unique=True, max_digits=2, decimal_places=0))

    def backwards(self, orm):

        # Changing field 'Page.orderid'
        db.alter_column('pages_page', 'orderid', self.gf('django.db.models.fields.DecimalField')(unique=True, max_digits=2, decimal_places=1))

    models = {
        'pages.page': {
            'Meta': {'object_name': 'Page'},
            'activated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'body': ('django.db.models.fields.TextField', [], {'default': '\'\\n    <div class="row">\\n    <div class="span12">\\n    <dib class="row">\\n    <div class="span3">\\n    <h3>Title 1</h3>\\n    <p>This is sample content</p>\\n    </div>\\n    <div class="span3">\\n    <h3>Title 2</h3>\\n    <p>This is sample content</p>\\n    </div>\\n    <div class="span3">\\n    <h3>Title</h3>\\n    <p>This is sample content</p>\\n    </div>\\n    </div>\\n    </div>\\n    </div>\\n    \'', 'max_length': '10000', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'display': ('django.db.models.fields.CharField', [], {'default': "'body'", 'max_length': '20'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'orderid': ('django.db.models.fields.DecimalField', [], {'unique': 'True', 'max_digits': '2', 'decimal_places': '0'}),
            'slug': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['pages']
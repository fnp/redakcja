# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Image.download_url'
        db.alter_column(u'cover_image', 'download_url', self.gf('django.db.models.fields.URLField')(max_length=200, unique=True, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Image.download_url'
        raise RuntimeError("Cannot reverse this migration. 'Image.download_url' and its values cannot be restored.")

    models = {
        u'cover.image': {
            'Meta': {'object_name': 'Image'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'download_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'unique': 'True', 'null': 'True'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'license_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['cover']
# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Image'
        db.create_table('cover_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('license_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('license_url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('download_url', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('file', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('cover', ['Image'])


    def backwards(self, orm):
        # Deleting model 'Image'
        db.delete_table('cover_image')


    models = {
        'cover.image': {
            'Meta': {'object_name': 'Image'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'download_url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'}),
            'file': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'license_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['cover']
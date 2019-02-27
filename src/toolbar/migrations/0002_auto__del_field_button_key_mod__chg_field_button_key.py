# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Deleting field 'Button.key_mod'
        db.delete_column('toolbar_button', 'key_mod')

        # Changing field 'Button.key'
        db.alter_column('toolbar_button', 'key', self.gf('django.db.models.fields.CharField')(max_length=1, null=True))

    def backwards(self, orm):

        # Adding field 'Button.key_mod'
        db.add_column('toolbar_button', 'key_mod', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, blank=True), keep_default=False)

        # Changing field 'Button.key'
        db.alter_column('toolbar_button', 'key', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True))

    models = {
        'toolbar.button': {
            'Meta': {'object_name': 'Button'},
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['toolbar.ButtonGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'scriptlet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['toolbar.Scriptlet']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tooltip': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'})
        },
        'toolbar.buttongroup': {
            'Meta': {'object_name': 'ButtonGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'toolbar.scriptlet': {
            'Meta': {'object_name': 'Scriptlet'},
            'code': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'})
        }
    }

    complete_apps = ['toolbar']

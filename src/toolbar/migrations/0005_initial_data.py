# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        from django.core.management import call_command
        call_command("loaddata", "initial_toolbar.yaml")


    def backwards(self, orm):
        "Write your backwards methods here."
        pass


    models = {
        'toolbar.button': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'Button'},
            'accesskey': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['toolbar.ButtonGroup']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'link': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'default': "'[]'"}),
            'scriptlet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['toolbar.Scriptlet']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'tooltip': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'})
        },
        'toolbar.buttongroup': {
            'Meta': {'ordering': "('position', 'name')", 'object_name': 'ButtonGroup'},
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

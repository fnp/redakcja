# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Theme'
        db.create_table('wiki_theme', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('wiki', ['Theme'])
        
        if not db.dry_run:
            from django.core.management import call_command
            call_command("loaddata", "initial_themes.yaml")

    
    
    def backwards(self, orm):
        
        # Deleting model 'Theme'
        db.delete_table('wiki_theme')
    
    
    models = {
        'wiki.theme': {
            'Meta': {'object_name': 'Theme'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }
    
    complete_apps = ['wiki']

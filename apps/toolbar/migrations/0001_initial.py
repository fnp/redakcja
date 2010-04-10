# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'ButtonGroup'
        db.create_table('toolbar_buttongroup', (
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('toolbar', ['ButtonGroup'])

        # Adding model 'Button'
        db.create_table('toolbar_button', (
            ('key_mod', self.gf('django.db.models.fields.PositiveIntegerField')(default=1, blank=True)),
            ('scriptlet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['toolbar.Scriptlet'], null=True, blank=True)),
            ('tooltip', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('link', self.gf('django.db.models.fields.CharField')(default='', max_length=256, blank=True)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=1, blank=True)),
            ('params', self.gf('django.db.models.fields.TextField')(default='[]')),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
        ))
        db.send_create_signal('toolbar', ['Button'])

        # Adding M2M table for field group on 'Button'
        db.create_table('toolbar_button_group', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('button', models.ForeignKey(orm['toolbar.button'], null=False)),
            ('buttongroup', models.ForeignKey(orm['toolbar.buttongroup'], null=False))
        ))
        db.create_unique('toolbar_button_group', ['button_id', 'buttongroup_id'])

        # Adding model 'Scriptlet'
        db.create_table('toolbar_scriptlet', (
            ('code', self.gf('django.db.models.fields.TextField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
        ))
        db.send_create_signal('toolbar', ['Scriptlet'])
    
    
    def backwards(self, orm):
        
        # Deleting model 'ButtonGroup'
        db.delete_table('toolbar_buttongroup')

        # Deleting model 'Button'
        db.delete_table('toolbar_button')

        # Removing M2M table for field group on 'Button'
        db.delete_table('toolbar_button_group')

        # Deleting model 'Scriptlet'
        db.delete_table('toolbar_scriptlet')
    
    
    models = {
        'toolbar.button': {
            'Meta': {'object_name': 'Button'},
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['toolbar.ButtonGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '1', 'blank': 'True'}),
            'key_mod': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1', 'blank': 'True'}),
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

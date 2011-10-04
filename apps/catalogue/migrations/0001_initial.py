# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Book'
        db.create_table('catalogue_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128, db_index=True)),
            ('gallery', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['catalogue.Book'])),
            ('parent_number', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('_short_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_single', self.gf('django.db.models.fields.NullBooleanField')(db_index=True, null=True, blank=True)),
            ('_new_publishable', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('_published', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal('catalogue', ['Book'])

        # Adding model 'Chunk'
        db.create_table('catalogue_chunk', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='created_documents', null=True, to=orm['auth.User'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.Book'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('_short_html', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('_hidden', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('_changed', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('stage', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.ChunkTag'], null=True, blank=True)),
            ('head', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['catalogue.ChunkChange'], null=True, blank=True)),
        ))
        db.send_create_signal('catalogue', ['Chunk'])

        # Adding unique constraint on 'Chunk', fields ['book', 'number']
        db.create_unique('catalogue_chunk', ['book_id', 'number'])

        # Adding unique constraint on 'Chunk', fields ['book', 'slug']
        db.create_unique('catalogue_chunk', ['book_id', 'slug'])

        # Adding model 'ChunkTag'
        db.create_table('catalogue_chunktag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('slug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=64, unique=True, null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('catalogue', ['ChunkTag'])

        # Adding model 'ChunkChange'
        db.create_table('catalogue_chunkchange', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('author_name', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('author_email', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('revision', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='children', null=True, blank=True, to=orm['catalogue.ChunkChange'])),
            ('merge_parent', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='merge_children', null=True, blank=True, to=orm['catalogue.ChunkChange'])),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('publishable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tree', self.gf('django.db.models.fields.related.ForeignKey')(related_name='change_set', to=orm['catalogue.Chunk'])),
            ('data', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal('catalogue', ['ChunkChange'])

        # Adding unique constraint on 'ChunkChange', fields ['tree', 'revision']
        db.create_unique('catalogue_chunkchange', ['tree_id', 'revision'])

        # Adding M2M table for field tags on 'ChunkChange'
        db.create_table('catalogue_chunkchange_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('chunkchange', models.ForeignKey(orm['catalogue.chunkchange'], null=False)),
            ('chunktag', models.ForeignKey(orm['catalogue.chunktag'], null=False))
        ))
        db.create_unique('catalogue_chunkchange_tags', ['chunkchange_id', 'chunktag_id'])

        # Adding model 'BookPublishRecord'
        db.create_table('catalogue_bookpublishrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(related_name='publish_log', to=orm['catalogue.Book'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('catalogue', ['BookPublishRecord'])

        # Adding model 'ChunkPublishRecord'
        db.create_table('catalogue_chunkpublishrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('book_record', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['catalogue.BookPublishRecord'])),
            ('change', self.gf('django.db.models.fields.related.ForeignKey')(related_name='publish_log', to=orm['catalogue.ChunkChange'])),
        ))
        db.send_create_signal('catalogue', ['ChunkPublishRecord'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'ChunkChange', fields ['tree', 'revision']
        db.delete_unique('catalogue_chunkchange', ['tree_id', 'revision'])

        # Removing unique constraint on 'Chunk', fields ['book', 'slug']
        db.delete_unique('catalogue_chunk', ['book_id', 'slug'])

        # Removing unique constraint on 'Chunk', fields ['book', 'number']
        db.delete_unique('catalogue_chunk', ['book_id', 'number'])

        # Deleting model 'Book'
        db.delete_table('catalogue_book')

        # Deleting model 'Chunk'
        db.delete_table('catalogue_chunk')

        # Deleting model 'ChunkTag'
        db.delete_table('catalogue_chunktag')

        # Deleting model 'ChunkChange'
        db.delete_table('catalogue_chunkchange')

        # Removing M2M table for field tags on 'ChunkChange'
        db.delete_table('catalogue_chunkchange_tags')

        # Deleting model 'BookPublishRecord'
        db.delete_table('catalogue_bookpublishrecord')

        # Deleting model 'ChunkPublishRecord'
        db.delete_table('catalogue_chunkpublishrecord')


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
        'catalogue.book': {
            'Meta': {'ordering': "['parent_number', 'title']", 'object_name': 'Book'},
            '_new_publishable': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            '_published': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            '_short_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            '_single': ('django.db.models.fields.NullBooleanField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'gallery': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['catalogue.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'catalogue.bookpublishrecord': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'BookPublishRecord'},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'publish_log'", 'to': "orm['catalogue.Book']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'catalogue.chunk': {
            'Meta': {'ordering': "['number']", 'unique_together': "[['book', 'number'], ['book', 'slug']]", 'object_name': 'Chunk'},
            '_changed': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            '_hidden': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            '_short_html': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.Book']"}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'created_documents'", 'null': 'True', 'to': "orm['auth.User']"}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['catalogue.ChunkChange']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'stage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.ChunkTag']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'catalogue.chunkchange': {
            'Meta': {'ordering': "('created_at',)", 'unique_together': "(['tree', 'revision'],)", 'object_name': 'ChunkChange'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'data': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merge_parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'merge_children'", 'null': 'True', 'blank': 'True', 'to': "orm['catalogue.ChunkChange']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': "orm['catalogue.ChunkChange']"}),
            'publishable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'change_set'", 'symmetrical': 'False', 'to': "orm['catalogue.ChunkTag']"}),
            'tree': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'change_set'", 'to': "orm['catalogue.Chunk']"})
        },
        'catalogue.chunkpublishrecord': {
            'Meta': {'object_name': 'ChunkPublishRecord'},
            'book_record': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['catalogue.BookPublishRecord']"}),
            'change': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'publish_log'", 'to': "orm['catalogue.ChunkChange']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'catalogue.chunktag': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'ChunkTag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '64', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['catalogue']

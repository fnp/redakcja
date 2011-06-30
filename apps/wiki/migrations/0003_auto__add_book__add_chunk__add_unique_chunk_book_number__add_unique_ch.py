# encoding: utf-8
import datetime
import os.path
import cPickle
import re
import urllib

from django.conf import settings
from django.db import models
from mercurial import mdiff, hg, ui
from south.db import db
from south.v2 import SchemaMigration

from slughifi import slughifi

META_REGEX = re.compile(r'\s*<!--\s(.*?)-->', re.DOTALL | re.MULTILINE)
STAGE_TAGS_RE = re.compile(r'^#stage-finished: (.*)$', re.MULTILINE)
AUTHOR_RE = re.compile(r'\s*(.*?)\s*<(.*)>\s*')


def urlunquote(url):
    """Unqotes URL

    # >>> urlunquote('Za%C5%BC%C3%B3%C5%82%C4%87_g%C4%99%C5%9Bl%C4%85_ja%C5%BA%C5%84')
    # u'Za\u017c\xf3\u0142\u0107_g\u0119\u015bl\u0105 ja\u017a\u0144'
    """
    return unicode(urllib.unquote(url), 'utf-8', 'ignore')


def split_name(name):
    parts = name.split('__')
    return parts


def file_to_title(fname):
    """ Returns a title-like version of a filename. """
    parts = (p.replace('_', ' ').title() for p in fname.split('__'))
    return ' / '.join(parts)


def make_patch(src, dst):
    if isinstance(src, unicode):
        src = src.encode('utf-8')
    if isinstance(dst, unicode):
        dst = dst.encode('utf-8')
    return cPickle.dumps(mdiff.textdiff(src, dst))


def plain_text(text):
    return re.sub(META_REGEX, '', text, 1)


def gallery(slug, text):
    result = {}

    m = re.match(META_REGEX, text)
    if m:
        for line in m.group(1).split('\n'):
            try:
                k, v = line.split(':', 1)
                result[k.strip()] = v.strip()
            except ValueError:
                continue

    gallery = result.get('gallery', slughifi(slug))

    if gallery.startswith('/'):
        gallery = os.path.basename(gallery)

    return gallery


def migrate_file_from_hg(orm, fname, entry):
    fname = urlunquote(fname)
    print fname
    if fname.endswith('.xml'):
        fname = fname[:-4]
    title = file_to_title(fname)
    fname = slughifi(fname)
    # create all the needed objects
    # what if it already exists?
    book = orm.Book.objects.create(
        title=title,
        slug=fname)
    chunk = orm.Chunk.objects.create(
        book=book,
        number=1,
        slug='1')
    head = orm['dvcs.Change'].objects.create(
        tree=chunk,
        revision=-1,
        patch=make_patch('', ''),
        created_at=datetime.datetime.fromtimestamp(entry.filectx(0).date()[0]),
        description=''
        )
    chunk.head = head
    try:
        chunk.stage = orm['dvcs.Tag'].objects.order_by('ordering')[0]
    except IndexError:
        chunk.stage = None
    old_data = ''

    maxrev = entry.filerev()
    gallery_link = None
    
    for rev in xrange(maxrev + 1):
        fctx = entry.filectx(rev)
        data = fctx.data()
        gallery_link = gallery(fname, data)
        data = plain_text(data)

        # get tags from description
        description = fctx.description().decode("utf-8", 'replace')
        tags = STAGE_TAGS_RE.findall(description)
        tags = [orm['dvcs.Tag'].objects.get(slug=slug.strip()) for slug in tags]

        if tags:
            max_ordering = max(tags, key=lambda x: x.ordering).ordering
            try:
                chunk.stage = orm['dvcs.Tag'].objects.filter(ordering__gt=max_ordering).order_by('ordering')[0]
            except IndexError:
                chunk.stage = None

        description = STAGE_TAGS_RE.sub('', description)

        author = author_name = author_email = None
        author_desc = fctx.user().decode("utf-8", 'replace')
        m = AUTHOR_RE.match(author_desc)
        if m:
            try:
                author = orm['auth.User'].objects.get(username=m.group(1), email=m.group(2))
            except orm['auth.User'].DoesNotExist:
                author_name = m.group(1)
                author_email = m.group(2)
        else:
            author_name = author_desc

        head = orm['dvcs.Change'].objects.create(
            tree=chunk,
            revision=rev + 1,
            patch=make_patch(old_data, data),
            created_at=datetime.datetime.fromtimestamp(fctx.date()[0]),
            description=description,
            author=author,
            author_name=author_name,
            author_email=author_email,
            parent=chunk.head
            )
        head.tags = tags
        chunk.head = head
        old_data = data

    chunk.save()
    if gallery_link:
        book.gallery = gallery_link
        book.save()


def migrate_from_hg(orm):
    try:
        hg_path = settings.WIKI_REPOSITORY_PATH
    except:
        pass

    print 'migrate from', hg_path
    repo = hg.repository(ui.ui(), hg_path)
    tip = repo['tip']
    for fname in tip:
        if fname.startswith('.'):
            continue
        migrate_file_from_hg(orm, fname, tip[fname])


class Migration(SchemaMigration):

    depends_on = [
        ('dvcs', '0001_initial'),
    ]

    def forwards(self, orm):
        
        # Adding model 'Book'
        db.create_table('wiki_book', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=128, db_index=True)),
            ('gallery', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['wiki.Book'])),
            ('parent_number', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('last_published', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('_list_html', self.gf('django.db.models.fields.TextField')(null=True)),
        ))
        db.send_create_signal('wiki', ['Book'])

        # Adding model 'Chunk'
        db.create_table('wiki_chunk', (
            ('document_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dvcs.Document'], unique=True, primary_key=True)),
            ('book', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['wiki.Book'])),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50, db_index=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('wiki', ['Chunk'])

        # Adding unique constraint on 'Chunk', fields ['book', 'number']
        db.create_unique('wiki_chunk', ['book_id', 'number'])

        # Adding unique constraint on 'Chunk', fields ['book', 'slug']
        db.create_unique('wiki_chunk', ['book_id', 'slug'])

        if not db.dry_run:
            migrate_from_hg(orm)

    def backwards(self, orm):
        
        # Removing unique constraint on 'Chunk', fields ['book', 'slug']
        db.delete_unique('wiki_chunk', ['book_id', 'slug'])

        # Removing unique constraint on 'Chunk', fields ['book', 'number']
        db.delete_unique('wiki_chunk', ['book_id', 'number'])

        # Deleting model 'Book'
        db.delete_table('wiki_book')

        # Deleting model 'Chunk'
        db.delete_table('wiki_chunk')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
        'dvcs.change': {
            'Meta': {'ordering': "('created_at',)", 'unique_together': "(['tree', 'revision'],)", 'object_name': 'Change'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'author_email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'author_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merge_parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'merge_children'", 'null': 'True', 'blank': 'True', 'to': "orm['dvcs.Change']"}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': "orm['dvcs.Change']"}),
            'patch': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'publishable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'revision': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['dvcs.Tag']", 'symmetrical': 'False'}),
            'tree': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dvcs.Document']"})
        },
        'dvcs.document': {
            'Meta': {'object_name': 'Document'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'head': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['dvcs.Change']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dvcs.Tag']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        },
        'dvcs.tag': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '64', 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        'wiki.book': {
            'Meta': {'ordering': "['parent_number', 'title']", 'object_name': 'Book'},
            '_list_html': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'gallery': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_published': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['wiki.Book']"}),
            'parent_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '128', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'wiki.chunk': {
            'Meta': {'ordering': "['number']", 'unique_together': "[['book', 'number'], ['book', 'slug']]", 'object_name': 'Chunk', '_ormbases': ['dvcs.Document']},
            'book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['wiki.Book']"}),
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'document_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['dvcs.Document']", 'unique': 'True', 'primary_key': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'wiki.theme': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Theme'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['wiki']

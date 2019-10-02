from django.db import models, migrations
import datetime
import django.db.models.deletion
from django.conf import settings
import dvcs.models
import dvcs.storage


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('cover', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='title', db_index=True)),
                ('slug', models.SlugField(unique=True, max_length=128, verbose_name='slug')),
                ('public', models.BooleanField(default=True, db_index=True, verbose_name='public')),
                ('gallery', models.CharField(max_length=255, verbose_name='scan gallery name', blank=True)),
                ('parent_number', models.IntegerField(db_index=True, verbose_name='parent number', null=True, editable=False, blank=True)),
                ('_short_html', models.TextField(null=True, editable=False, blank=True)),
                ('_single', models.NullBooleanField(db_index=True, editable=False)),
                ('_new_publishable', models.NullBooleanField(editable=False)),
                ('_published', models.NullBooleanField(editable=False)),
                ('_on_track', models.IntegerField(db_index=True, null=True, editable=False, blank=True)),
                ('dc_slug', models.CharField(db_index=True, max_length=128, null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ['title', 'slug'],
                'verbose_name': 'book',
                'verbose_name_plural': 'books',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookPublishRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('book', models.ForeignKey(related_name='publish_log', verbose_name='book', to='catalogue.Book', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'book publish record',
                'verbose_name_plural': 'book publish records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.IntegerField(verbose_name='number')),
                ('title', models.CharField(max_length=255, verbose_name='title', blank=True)),
                ('slug', models.SlugField(verbose_name='slug')),
                ('gallery_start', models.IntegerField(default=1, null=True, verbose_name='gallery start', blank=True)),
                ('_short_html', models.TextField(null=True, editable=False, blank=True)),
                ('_hidden', models.NullBooleanField(editable=False)),
                ('_changed', models.NullBooleanField(editable=False)),
                ('book', models.ForeignKey(editable=False, to='catalogue.Book', verbose_name='book', on_delete=models.CASCADE)),
                ('creator', models.ForeignKey(related_name='created_chunk', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='creator', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['number'],
                'verbose_name': 'chunk',
                'verbose_name_plural': 'chunks',
                'permissions': [('can_pubmark', 'Can mark for publishing')],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChunkChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name', blank=True)),
                ('author_email', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email', blank=True)),
                ('revision', models.IntegerField(verbose_name='revision', db_index=True)),
                ('description', models.TextField(default=b'', verbose_name='description', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, editable=False, db_index=True)),
                ('publishable', models.BooleanField(default=False, verbose_name='publishable')),
                ('data', models.FileField(upload_to=dvcs.models.data_upload_to, storage=dvcs.storage.GzipFileSystemStorage(location=settings.CATALOGUE_REPO_PATH), verbose_name='data')),
                ('author', models.ForeignKey(verbose_name='author', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('merge_parent', models.ForeignKey(related_name='merge_children', default=None, blank=True, to='catalogue.ChunkChange', null=True, verbose_name='merge parent', on_delete=models.CASCADE)),
                ('parent', models.ForeignKey(related_name='children', default=None, blank=True, to='catalogue.ChunkChange', null=True, verbose_name='parent', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('created_at',),
                'abstract': False,
                'verbose_name': 'change for: chunk',
                'verbose_name_plural': 'changes for: chunk',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChunkPublishRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('book_record', models.ForeignKey(verbose_name='book publish record', to='catalogue.BookPublishRecord', on_delete=models.CASCADE)),
                ('change', models.ForeignKey(related_name='publish_log', verbose_name='change', to='catalogue.ChunkChange', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'chunk publish record',
                'verbose_name_plural': 'chunk publish records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChunkTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('slug', models.SlugField(null=True, max_length=64, blank=True, unique=True, verbose_name='slug')),
                ('ordering', models.IntegerField(verbose_name='ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'abstract': False,
                'verbose_name': 'tag for: chunk',
                'verbose_name_plural': 'tags for: chunk',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.FileField(upload_to=b'catalogue/images', verbose_name='image')),
                ('title', models.CharField(max_length=255, verbose_name='title', blank=True)),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('public', models.BooleanField(default=True, db_index=True, verbose_name='public')),
                ('_short_html', models.TextField(null=True, editable=False, blank=True)),
                ('_new_publishable', models.NullBooleanField(editable=False)),
                ('_published', models.NullBooleanField(editable=False)),
                ('_changed', models.NullBooleanField(editable=False)),
                ('creator', models.ForeignKey(related_name='created_image', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True, verbose_name='creator', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
                'permissions': [('can_pubmark_image', 'Can mark images for publishing')],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name', blank=True)),
                ('author_email', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email', blank=True)),
                ('revision', models.IntegerField(verbose_name='revision', db_index=True)),
                ('description', models.TextField(default=b'', verbose_name='description', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, editable=False, db_index=True)),
                ('publishable', models.BooleanField(default=False, verbose_name='publishable')),
                ('data', models.FileField(upload_to=dvcs.models.data_upload_to, storage=dvcs.storage.GzipFileSystemStorage(location=settings.CATALOGUE_IMAGE_REPO_PATH), verbose_name='data')),
                ('author', models.ForeignKey(verbose_name='author', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('merge_parent', models.ForeignKey(related_name='merge_children', default=None, blank=True, to='catalogue.ImageChange', null=True, verbose_name='merge parent', on_delete=models.CASCADE)),
                ('parent', models.ForeignKey(related_name='children', default=None, blank=True, to='catalogue.ImageChange', null=True, verbose_name='parent', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('created_at',),
                'abstract': False,
                'verbose_name': 'change for: image',
                'verbose_name_plural': 'changes for: image',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImagePublishRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('change', models.ForeignKey(related_name='publish_log', verbose_name='change', to='catalogue.ImageChange', on_delete=models.CASCADE)),
                ('image', models.ForeignKey(related_name='publish_log', verbose_name='image', to='catalogue.Image', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'image publish record',
                'verbose_name_plural': 'image publish records',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('slug', models.SlugField(null=True, max_length=64, blank=True, unique=True, verbose_name='slug')),
                ('ordering', models.IntegerField(verbose_name='ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'abstract': False,
                'verbose_name': 'tag for: image',
                'verbose_name_plural': 'tags for: image',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='name')),
                ('notes', models.TextField(null=True, verbose_name='notes', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='imagechange',
            name='tags',
            field=models.ManyToManyField(related_name='change_set', verbose_name='tags', to='catalogue.ImageTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imagechange',
            name='tree',
            field=models.ForeignKey(related_name='change_set', verbose_name='document', to='catalogue.Image', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='imagechange',
            unique_together=set([('tree', 'revision')]),
        ),
        migrations.AddField(
            model_name='image',
            name='head',
            field=models.ForeignKey(default=None, editable=False, to='catalogue.ImageChange', blank=True, help_text="This document's current head.", null=True, verbose_name='head', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='project',
            field=models.ForeignKey(blank=True, to='catalogue.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='stage',
            field=models.ForeignKey(verbose_name='stage', blank=True, to='catalogue.ImageTag', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Work assignment.', null=True, verbose_name='user', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chunkchange',
            name='tags',
            field=models.ManyToManyField(related_name='change_set', verbose_name='tags', to='catalogue.ChunkTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chunkchange',
            name='tree',
            field=models.ForeignKey(related_name='change_set', verbose_name='document', to='catalogue.Chunk', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='chunkchange',
            unique_together=set([('tree', 'revision')]),
        ),
        migrations.AddField(
            model_name='chunk',
            name='head',
            field=models.ForeignKey(default=None, editable=False, to='catalogue.ChunkChange', blank=True, help_text="This document's current head.", null=True, verbose_name='head', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chunk',
            name='stage',
            field=models.ForeignKey(verbose_name='stage', blank=True, to='catalogue.ChunkTag', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='chunk',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text='Work assignment.', null=True, verbose_name='user', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='chunk',
            unique_together=set([('book', 'number'), ('book', 'slug')]),
        ),
        migrations.AddField(
            model_name='book',
            name='dc_cover_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, editable=False, to='cover.Image', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='book',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, editable=False, to='catalogue.Book', null=True, verbose_name='parent', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='book',
            name='project',
            field=models.ForeignKey(blank=True, to='catalogue.Project', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
    ]

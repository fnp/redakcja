# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
"""
Adds all of the models previously in `catalogue` app.
This is purely a state migration. If at any point a decisiion
is made to remove previous `catalogue` migrations, this will need
to be converted to a real database migration.
"""

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import dvcs.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cover', '0002_auto_20191002_1224'),
        ('catalogue', '0005_auto_20200322_2114'),
    ]

    _state_operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255, verbose_name='title')),
                ('slug', models.SlugField(max_length=128, unique=True, verbose_name='slug')),
                ('public', models.BooleanField(db_index=True, default=True, verbose_name='public')),
                ('gallery', models.CharField(blank=True, max_length=255, verbose_name='scan gallery name')),
                ('parent_number', models.IntegerField(blank=True, db_index=True, editable=False, null=True, verbose_name='parent number')),
                ('_single', models.NullBooleanField(db_index=True, editable=False)),
                ('_new_publishable', models.NullBooleanField(editable=False)),
                ('_published', models.NullBooleanField(editable=False)),
                ('_on_track', models.IntegerField(blank=True, db_index=True, editable=False, null=True)),
                ('dc_slug', models.CharField(blank=True, db_index=True, editable=False, max_length=128, null=True)),
                ('dc_cover_image', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='cover.Image')),
                ('parent', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='documents.Book', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'book',
                'verbose_name_plural': 'books',
                'db_table': 'catalogue_book',
                'ordering': ['title', 'slug'],
            },
        ),
        migrations.CreateModel(
            name='BookPublishRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_log', to='documents.Book', verbose_name='book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'book publish record',
                'verbose_name_plural': 'book publish records',
                'db_table': 'catalogue_bookpublishrecord',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(verbose_name='number')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='title')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('gallery_start', models.IntegerField(blank=True, default=1, null=True, verbose_name='gallery start')),
                ('_hidden', models.NullBooleanField(editable=False)),
                ('_changed', models.NullBooleanField(editable=False)),
                ('_new_publishable', models.NullBooleanField(editable=False)),
                ('book', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='documents.Book', verbose_name='book')),
                ('creator', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_chunk', to=settings.AUTH_USER_MODEL, verbose_name='creator')),
            ],
            options={
                'verbose_name': 'chunk',
                'verbose_name_plural': 'chunks',
                'db_table': 'catalogue_chunk',
                'ordering': ['number'],
                'permissions': [('can_pubmark', 'Can mark for publishing')],
            },
        ),
        migrations.CreateModel(
            name='ChunkChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name')),
                ('author_email', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email')),
                ('revision', models.IntegerField(db_index=True, verbose_name='revision')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('created_at', models.DateTimeField(db_index=True, default=datetime.datetime.now, editable=False)),
                ('publishable', models.BooleanField(default=False, verbose_name='publishable')),
                ('data', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/rczajka/for/fnp/redakcja/var/repo'), upload_to=dvcs.models.data_upload_to, verbose_name='data')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('merge_parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='merge_children', to='documents.ChunkChange', verbose_name='merge parent')),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='documents.ChunkChange', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'change for: chunk',
                'verbose_name_plural': 'changes for: chunk',
                'db_table': 'catalogue_chunkchange',
                'ordering': ('created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ChunkTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('slug', models.SlugField(blank=True, max_length=64, null=True, unique=True, verbose_name='slug')),
                ('ordering', models.IntegerField(verbose_name='ordering')),
            ],
            options={
                'verbose_name': 'tag for: chunk',
                'verbose_name_plural': 'tags for: chunk',
                'db_table': 'catalogue_chunktag',
                'ordering': ['ordering'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='catalogue/images', verbose_name='image')),
                ('title', models.CharField(blank=True, max_length=255, verbose_name='title')),
                ('slug', models.SlugField(unique=True, verbose_name='slug')),
                ('public', models.BooleanField(db_index=True, default=True, verbose_name='public')),
                ('_new_publishable', models.NullBooleanField(editable=False)),
                ('_published', models.NullBooleanField(editable=False)),
                ('_changed', models.NullBooleanField(editable=False)),
                ('creator', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_image', to=settings.AUTH_USER_MODEL, verbose_name='creator')),
            ],
            options={
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
                'db_table': 'catalogue_image',
                'ordering': ['title'],
                'permissions': [('can_pubmark_image', 'Can mark images for publishing')],
            },
        ),
        migrations.CreateModel(
            name='ImageChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name')),
                ('author_email', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email')),
                ('revision', models.IntegerField(db_index=True, verbose_name='revision')),
                ('description', models.TextField(blank=True, default='', verbose_name='description')),
                ('created_at', models.DateTimeField(db_index=True, default=datetime.datetime.now, editable=False)),
                ('publishable', models.BooleanField(default=False, verbose_name='publishable')),
                ('data', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='/home/rczajka/for/fnp/redakcja/var/imgrepo'), upload_to=dvcs.models.data_upload_to, verbose_name='data')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('merge_parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='merge_children', to='documents.ImageChange', verbose_name='merge parent')),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='documents.ImageChange', verbose_name='parent')),
            ],
            options={
                'verbose_name': 'change for: image',
                'verbose_name_plural': 'changes for: image',
                'db_table': 'catalogue_imagechange',
                'ordering': ('created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('slug', models.SlugField(blank=True, max_length=64, null=True, unique=True, verbose_name='slug')),
                ('ordering', models.IntegerField(verbose_name='ordering')),
            ],
            options={
                'verbose_name': 'tag for: image',
                'verbose_name_plural': 'tags for: image',
                'db_table': 'catalogue_imagetag',
                'ordering': ['ordering'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='name')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='notes')),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
                'db_table': 'catalogue_project',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ImagePublishRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('change', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_log', to='documents.ImageChange', verbose_name='change')),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_log', to='documents.Image', verbose_name='image')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'image publish record',
                'verbose_name_plural': 'image publish records',
                'db_table': 'catalogue_imagepublishrecord',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddField(
            model_name='imagechange',
            name='tags',
            field=models.ManyToManyField(related_name='change_set', to='documents.ImageTag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='imagechange',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_set', to='documents.Image', verbose_name='document'),
        ),
        migrations.AddField(
            model_name='image',
            name='head',
            field=models.ForeignKey(blank=True, default=None, editable=False, help_text="This document's current head.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.ImageChange', verbose_name='head'),
        ),
        migrations.AddField(
            model_name='image',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.Project'),
        ),
        migrations.AddField(
            model_name='image',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.ImageTag', verbose_name='stage'),
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Work assignment.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.CreateModel(
            name='ChunkPublishRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='documents.BookPublishRecord', verbose_name='book publish record')),
                ('change', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='publish_log', to='documents.ChunkChange', verbose_name='change')),
            ],
            options={
                'verbose_name': 'chunk publish record',
                'verbose_name_plural': 'chunk publish records',
                'db_table': 'catalogue_chunkpublishrecord',
            },
        ),
        migrations.AddField(
            model_name='chunkchange',
            name='tags',
            field=models.ManyToManyField(related_name='change_set', to='documents.ChunkTag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='chunkchange',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_set', to='documents.Chunk', verbose_name='document'),
        ),
        migrations.AddField(
            model_name='chunk',
            name='head',
            field=models.ForeignKey(blank=True, default=None, editable=False, help_text="This document's current head.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.ChunkChange', verbose_name='head'),
        ),
        migrations.AddField(
            model_name='chunk',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.ChunkTag', verbose_name='stage'),
        ),
        migrations.AddField(
            model_name='chunk',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Work assignment.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='book',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='documents.Project'),
        ),
        migrations.AlterUniqueTogether(
            name='imagechange',
            unique_together={('tree', 'revision')},
        ),
        migrations.AlterUniqueTogether(
            name='chunkchange',
            unique_together={('tree', 'revision')},
        ),
        migrations.AlterUniqueTogether(
            name='chunk',
            unique_together={('book', 'slug'), ('book', 'number')},
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=_state_operations,
        )
    ]

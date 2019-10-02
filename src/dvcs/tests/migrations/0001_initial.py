# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import datetime
import os.path
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import dvcs.models
import dvcs.storage


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ADocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_adocument', to=settings.AUTH_USER_MODEL, verbose_name='creator')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ADocumentChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name')),
                ('author_email', models.CharField(blank=True, help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email')),
                ('revision', models.IntegerField(db_index=True, verbose_name='revision')),
                ('description', models.TextField(blank=True, default=b'', verbose_name='description')),
                ('created_at', models.DateTimeField(db_index=True, default=datetime.datetime.now, editable=False)),
                ('publishable', models.BooleanField(default=False, verbose_name='publishable')),
                ('data', models.FileField(storage=dvcs.storage.GzipFileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'dvcs')), upload_to=dvcs.models.data_upload_to, verbose_name='data')),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('merge_parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='merge_children', to='tests.ADocumentChange', verbose_name='merge parent')),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tests.ADocumentChange', verbose_name='parent')),
            ],
            options={
                'ordering': ('created_at',),
                'abstract': False,
                'verbose_name': 'change for: a document',
                'verbose_name_plural': 'changes for: a document',
            },
        ),
        migrations.CreateModel(
            name='ADocumentTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='name')),
                ('slug', models.SlugField(blank=True, max_length=64, null=True, unique=True, verbose_name='slug')),
                ('ordering', models.IntegerField(verbose_name='ordering')),
            ],
            options={
                'ordering': ['ordering'],
                'abstract': False,
                'verbose_name': 'tag for: a document',
                'verbose_name_plural': 'tags for: a document',
            },
        ),
        migrations.AddField(
            model_name='adocumentchange',
            name='tags',
            field=models.ManyToManyField(related_name='change_set', to='tests.ADocumentTag', verbose_name='tags'),
        ),
        migrations.AddField(
            model_name='adocumentchange',
            name='tree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_set', to='tests.ADocument', verbose_name='document'),
        ),
        migrations.AddField(
            model_name='adocument',
            name='head',
            field=models.ForeignKey(blank=True, default=None, editable=False, help_text="This document's current head.", null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.ADocumentChange', verbose_name='head'),
        ),
        migrations.AddField(
            model_name='adocument',
            name='stage',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tests.ADocumentTag', verbose_name='stage'),
        ),
        migrations.AddField(
            model_name='adocument',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Work assignment.', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterUniqueTogether(
            name='adocumentchange',
            unique_together=set([('tree', 'revision')]),
        ),
    ]

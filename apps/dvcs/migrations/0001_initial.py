# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ref',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Revision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author_name', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author name', blank=True)),
                ('author_email', models.CharField(help_text='Used if author is not set.', max_length=128, null=True, verbose_name='author email', blank=True)),
                ('description', models.TextField(default='', verbose_name='description', blank=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, editable=False, db_index=True)),
                ('author', models.ForeignKey(verbose_name='author', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('merge_parent', models.ForeignKey(related_name='merge_children', default=None, blank=True, to='dvcs.Revision', null=True, verbose_name='merge parent')),
                ('parent', models.ForeignKey(related_name='children', default=None, blank=True, to='dvcs.Revision', null=True, verbose_name='parent')),
            ],
            options={
                'ordering': ('created_at',),
                'verbose_name': 'revision',
                'verbose_name_plural': 'revisions',
            },
        ),
        migrations.AddField(
            model_name='ref',
            name='revision',
            field=models.ForeignKey(default=None, editable=False, to='dvcs.Revision', blank=True, help_text="The document's revision.", null=True, verbose_name='revision'),
        ),
    ]

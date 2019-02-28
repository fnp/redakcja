# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cover.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('author', models.CharField(max_length=255, verbose_name='author')),
                ('license_name', models.CharField(max_length=255, verbose_name='license name')),
                ('license_url', models.URLField(max_length=255, verbose_name='license URL', blank=True)),
                ('source_url', models.URLField(null=True, verbose_name='source URL', blank=True)),
                ('download_url', models.URLField(unique=True, null=True, verbose_name='image download URL', blank=True)),
                ('file', models.ImageField(upload_to=b'cover/image', storage=cover.models.OverwriteStorage(), verbose_name='file')),
            ],
            options={
                'verbose_name': 'cover image',
                'verbose_name_plural': 'cover images',
            },
            bases=(models.Model,),
        ),
    ]

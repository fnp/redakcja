# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Button',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=32)),
                ('slug', models.SlugField(unique=True)),
                ('params', models.TextField(default=b'[]')),
                ('link', models.CharField(default=b'', max_length=256, blank=True)),
                ('accesskey', models.CharField(max_length=1, blank=True)),
                ('tooltip', models.CharField(max_length=120, blank=True)),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'button',
                'verbose_name_plural': 'buttons',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ButtonGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('slug', models.SlugField()),
                ('position', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('position', 'name'),
                'verbose_name': 'button group',
                'verbose_name_plural': 'button groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Scriptlet',
            fields=[
                ('name', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('code', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='button',
            name='group',
            field=models.ManyToManyField(to='toolbar.ButtonGroup'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='button',
            name='scriptlet',
            field=models.ForeignKey(blank=True, to='toolbar.Scriptlet', null=True),
            preserve_default=True,
        ),
    ]

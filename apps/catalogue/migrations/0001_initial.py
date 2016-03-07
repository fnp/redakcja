# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dvcs', '__first__'),
        ('organizations', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('ref_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='dvcs.Ref')),
                ('stage', models.CharField(default='', max_length=128, verbose_name='stage', blank=True)),
                ('owner_organization', models.ForeignKey(to='organizations.Organization', null=True)),
            ],
            options={
                'verbose_name': 'document',
                'verbose_name_plural': 'documents',
            },
            bases=('dvcs.ref',),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('is_main', models.BooleanField()),
                ('is_partial', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
            managers=[
                (b'objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='owner_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]

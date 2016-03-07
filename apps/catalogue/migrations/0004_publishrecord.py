# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dvcs', '0001_initial'),
        ('catalogue', '0003_plan'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublishRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('document', models.ForeignKey(related_name='publish_log', verbose_name='document', to='catalogue.Document')),
                ('revision', models.ForeignKey(related_name='publish_log', verbose_name='revision', to='dvcs.Revision')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'book publish records',
            },
        ),
    ]

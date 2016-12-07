# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('key', models.CharField(help_text='A unique name for this attachment', max_length=255, serialize=False, verbose_name='key', primary_key=True)),
                ('attachment', models.FileField(upload_to=b'attachment')),
            ],
            options={
                'ordering': ('key',),
                'verbose_name': 'attachment',
                'verbose_name_plural': 'attachments',
            },
        ),
    ]

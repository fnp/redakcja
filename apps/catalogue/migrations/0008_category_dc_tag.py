# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_document_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='dc_tag',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]

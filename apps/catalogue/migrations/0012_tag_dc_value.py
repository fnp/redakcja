# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0011_document_published'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='dc_value',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]

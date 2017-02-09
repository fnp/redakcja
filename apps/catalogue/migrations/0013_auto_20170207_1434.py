# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_tag_dc_value'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['index'], 'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['index', 'label'], 'verbose_name': 'tag', 'verbose_name_plural': 'tags'},
        ),
        migrations.AddField(
            model_name='category',
            name='multiple',
            field=models.BooleanField(default=False, verbose_name='multiple choice'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20161130_1346'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='publishrecord',
            options={'ordering': ['-timestamp'], 'verbose_name': 'book publish record', 'verbose_name_plural': 'book publish records'},
        ),
        migrations.AlterField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(to='catalogue.Tag', blank=True),
        ),
    ]

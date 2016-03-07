# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0002_auto_20150408_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, max_length=64, choices=[('intl', 'International'), ('de', 'Germany'), ('gr', 'Greece'), ('pl', 'Poland')]),
        ),
        migrations.AlterField(
            model_name='organization',
            name='projects',
            field=models.TextField(default='', blank=True),
        ),
    ]

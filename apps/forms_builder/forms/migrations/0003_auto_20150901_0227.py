# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0002_auto_20150819_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='label',
            field=models.CharField(verbose_name='Label', max_length=2048),
        ),
        migrations.AlterField(
            model_name='form',
            name='slug',
            field=models.SlugField(unique=True, verbose_name='Slug', max_length=100),
        ),
    ]

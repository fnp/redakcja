# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0004_publishrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='document',
            name='stage',
            field=models.CharField(default=b'Draft', max_length=128, verbose_name='stage', blank=True),
        ),
    ]

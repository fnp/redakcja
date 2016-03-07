# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='description',
        ),
        migrations.AddField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, max_length=64, choices=[('intl', 'International'), ('de', 'Germany'), ('pl', 'Poland')]),
        ),
        migrations.AddField(
            model_name='organization',
            name='projects',
            field=jsonfield.fields.JSONField(default=[]),
        ),
        migrations.AddField(
            model_name='organization',
            name='www',
            field=models.URLField(blank=True),
        ),
    ]

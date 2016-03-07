# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0003_auto_20150417_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='preview_html',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, max_length=64, choices=[('intl', 'International'), ('be', 'Belgium'), ('de', 'Germany'), ('gr', 'Greece'), ('pl', 'Poland')]),
        ),
    ]

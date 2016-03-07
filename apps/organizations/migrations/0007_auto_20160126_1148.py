# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0006_auto_20150601_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='preview_html_pl',
            field=models.TextField(default='', blank=True),
        ),
        migrations.AddField(
            model_name='usercard',
            name='preview_html_pl',
            field=models.TextField(default='', blank=True),
        ),
    ]

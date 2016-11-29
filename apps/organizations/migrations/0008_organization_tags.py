# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_document_tags'),
        ('organizations', '0007_auto_20160126_1148'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='tags',
            field=models.ManyToManyField(to='catalogue.Tag'),
        ),
    ]

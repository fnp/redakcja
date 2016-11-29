# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0006_category_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(to='catalogue.Tag'),
        ),
    ]

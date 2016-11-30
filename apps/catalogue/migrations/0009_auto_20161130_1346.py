# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_category_dc_tag'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['index']},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['index']},
        ),
    ]

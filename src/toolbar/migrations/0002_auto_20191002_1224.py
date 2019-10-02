# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('toolbar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='button',
            name='link',
            field=models.CharField(blank=True, default='', max_length=256),
        ),
        migrations.AlterField(
            model_name='button',
            name='params',
            field=models.TextField(default='[]'),
        ),
        migrations.AlterField(
            model_name='button',
            name='scriptlet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='toolbar.Scriptlet'),
        ),
    ]

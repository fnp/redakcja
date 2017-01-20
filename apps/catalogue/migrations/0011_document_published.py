# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def set_published(apps, schema_editor):
    Document = apps.get_model('catalogue', 'Document')
    Document.objects.exclude(publish_log=None).update(published=True)


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20170119_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(set_published),
    ]

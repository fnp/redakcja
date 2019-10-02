# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='_short_html',
        ),
        migrations.RemoveField(
            model_name='chunk',
            name='_short_html',
        ),
        migrations.RemoveField(
            model_name='image',
            name='_short_html',
        ),
    ]

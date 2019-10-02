# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0002_auto_20190307_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='_new_publishable',
            field=models.NullBooleanField(editable=False),
        ),
    ]

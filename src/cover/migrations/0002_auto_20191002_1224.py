# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
import cover.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cover', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(storage=cover.models.OverwriteStorage(), upload_to='cover/image', verbose_name='file'),
        ),
    ]

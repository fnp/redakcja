# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0008_organization_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='tags',
            field=models.ManyToManyField(to='catalogue.Tag', blank=True),
        ),
        migrations.AlterField(
            model_name='usercard',
            name='user',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]

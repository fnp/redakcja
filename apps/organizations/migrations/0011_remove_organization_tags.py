# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 11:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0010_auto_20170216_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='tags',
        ),
    ]
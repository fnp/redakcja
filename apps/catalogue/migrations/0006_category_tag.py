# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0005_auto_20150505_1229'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=64, verbose_name='category')),
                ('label_en', models.CharField(max_length=64, null=True, verbose_name='category')),
                ('label_pl', models.CharField(max_length=64, null=True, verbose_name='category')),
                ('index', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=64, verbose_name='tag')),
                ('label_en', models.CharField(max_length=64, null=True, verbose_name='tag')),
                ('label_pl', models.CharField(max_length=64, null=True, verbose_name='tag')),
                ('index', models.IntegerField()),
                ('category', models.ForeignKey(to='catalogue.Category')),
            ],
        ),
    ]

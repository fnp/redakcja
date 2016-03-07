# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('organizations', '0005_organization_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCard',
            fields=[
                ('logo', models.ImageField(upload_to='people/logo', blank=True)),
                ('country', models.CharField(blank=True, max_length=64, choices=[('intl', 'International'), ('at', 'Austria'), ('be', 'Belgium'), ('gb', 'Bulgaria'), ('hr', 'Croatia'), ('cy', 'Cyprus'), ('cz', 'Czech Republic'), ('dk', 'Denmark'), ('ee', 'Estonia'), ('fi', 'Finland'), ('fr', 'France'), ('de', 'Germany'), ('gr', 'Greece'), ('hu', 'Hungary'), ('ie', 'Ireland'), ('it', 'Italy'), ('lv', 'Latvia'), ('lt', 'Lithuania'), ('lu', 'Luxembourg'), ('mt', 'Malta'), ('nl', 'Netherlands'), ('pl', 'Poland'), ('pt', 'Portugal'), ('ro', 'Romania'), ('sk', 'Slovakia'), ('si', 'Slovenia'), ('es', 'Spain'), ('se', 'Sweden'), ('uk', 'United Kingdom')])),
                ('www', models.URLField(blank=True)),
                ('description', models.TextField(default='', blank=True)),
                ('projects', models.TextField(default='', blank=True)),
                ('preview_html', models.TextField(default='', blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='organization',
            name='country',
            field=models.CharField(blank=True, max_length=64, choices=[('intl', 'International'), ('at', 'Austria'), ('be', 'Belgium'), ('gb', 'Bulgaria'), ('hr', 'Croatia'), ('cy', 'Cyprus'), ('cz', 'Czech Republic'), ('dk', 'Denmark'), ('ee', 'Estonia'), ('fi', 'Finland'), ('fr', 'France'), ('de', 'Germany'), ('gr', 'Greece'), ('hu', 'Hungary'), ('ie', 'Ireland'), ('it', 'Italy'), ('lv', 'Latvia'), ('lt', 'Lithuania'), ('lu', 'Luxembourg'), ('mt', 'Malta'), ('nl', 'Netherlands'), ('pl', 'Poland'), ('pt', 'Portugal'), ('ro', 'Romania'), ('sk', 'Slovakia'), ('si', 'Slovenia'), ('es', 'Spain'), ('se', 'Sweden'), ('uk', 'United Kingdom')]),
        ),
    ]

# Generated by Django 4.0.6 on 2022-09-19 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0030_auto_20210706_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='place_of_birth',
            field=models.CharField(blank=True, max_length=255, verbose_name='place of birth'),
        ),
        migrations.AddField(
            model_name='author',
            name='place_of_death',
            field=models.CharField(blank=True, max_length=255, verbose_name='place of death'),
        ),
        migrations.AddField(
            model_name='author',
            name='year_of_birth',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='year of birth'),
        ),
    ]
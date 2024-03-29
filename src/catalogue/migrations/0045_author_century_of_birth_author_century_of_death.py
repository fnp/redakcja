# Generated by Django 4.0.6 on 2023-01-27 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0044_epoch_description_genre_description_kind_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='century_of_birth',
            field=models.SmallIntegerField(blank=True, help_text='Set if year unknown. Negative for BC.', null=True, verbose_name='century of birth'),
        ),
        migrations.AddField(
            model_name='author',
            name='century_of_death',
            field=models.SmallIntegerField(blank=True, help_text='Set if year unknown. Negative for BC.', null=True, verbose_name='century of death'),
        ),
    ]

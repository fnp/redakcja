# Generated by Django 3.0.4 on 2020-11-02 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0003_auto_20201102_1324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='dc_slug',
            new_name='catalogue_book',
        ),
    ]

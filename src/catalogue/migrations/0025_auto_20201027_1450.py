# Generated by Django 3.0.4 on 2020-10-27 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0024_workrate_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='estimate_source',
            field=models.CharField(blank=True, max_length=2048),
        ),
        migrations.AddField(
            model_name='book',
            name='estimated_chars',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='estimated_verses',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
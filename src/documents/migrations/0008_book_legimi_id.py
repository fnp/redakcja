# Generated by Django 3.2.12 on 2022-03-15 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0007_book_dc'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='legimi_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

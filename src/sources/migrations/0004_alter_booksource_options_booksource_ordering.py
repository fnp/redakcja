# Generated by Django 4.1.9 on 2024-05-22 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sources", "0003_source_modified_at_source_processed_at"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="booksource",
            options={"ordering": ("ordering", "page_start")},
        ),
        migrations.AddField(
            model_name="booksource",
            name="ordering",
            field=models.IntegerField(default=1),
        ),
    ]

# Generated by Django 4.1.9 on 2023-07-24 16:33

import cover.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cover", "0005_alter_image_download_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="image",
            name="example",
            field=models.ImageField(
                default="",
                editable=False,
                storage=cover.models.OverwriteStorage(),
                upload_to="cover/example",
            ),
            preserve_default=False,
        ),
    ]

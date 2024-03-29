# Generated by Django 4.1.9 on 2024-01-30 16:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0013_alter_chunkchange_publishable_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="logo",
            field=models.FileField(blank=True, upload_to="projects"),
        ),
        migrations.AddField(
            model_name="project",
            name="logo_mono",
            field=models.FileField(
                blank=True, help_text="white on transparent", upload_to="logo_mono"
            ),
        ),
    ]

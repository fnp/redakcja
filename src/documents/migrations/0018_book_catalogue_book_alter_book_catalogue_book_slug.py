# Generated by Django 4.1.9 on 2024-10-15 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("catalogue", "0055_book_parent_book_parent_number_editornote"),
        ("documents", "0017_rename_catalogue_book"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="catalogue_book",
            field=models.ForeignKey(
                blank=True,
                null=True,
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="document_books",
                related_query_name="document_book",
                to="catalogue.book",
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="dc_slug",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                editable=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="document_books_by_slug",
                related_query_name="document_book_by_slug",
                to="catalogue.book",
                to_field="slug",
            ),
        ),
    ]

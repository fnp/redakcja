# Generated by Django 4.1.9 on 2024-10-15 14:23

from django.db import migrations


def copy_slug_to_fk(apps, schema_editor):
    cBook = apps.get_model('catalogue', 'Book')
    dBook = apps.get_model('documents', 'Book')

    for db in dBook.objects.all():
        try:
            cb = db.dc_slug
        except cBook.DoesNotExist:
            pass
        else:
            if cb is not None:
                db.catalogue_book = cb
                db.save()


class Migration(migrations.Migration):

    dependencies = [
        ("documents", "0018_book_catalogue_book_alter_book_catalogue_book_slug"),
    ]

    operations = [
        migrations.RunPython(
            copy_slug_to_fk,
            migrations.RunPython.noop,
        )
    ]

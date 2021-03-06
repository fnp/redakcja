# Generated by Django 3.0.4 on 2020-04-10 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0007_auto_20200322_2326'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='name',
            new_name='last_name',
        ),
        migrations.RemoveField(
            model_name='book',
            name='translator',
        ),
        migrations.RemoveField(
            model_name='book',
            name='uri',
        ),
        migrations.AddField(
            model_name='author',
            name='first_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='author',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='author',
            name='priority',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Low'), (1, 'Medium'), (2, 'High')], default=0),
        ),
        migrations.AddField(
            model_name='author',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='author',
            name='wikidata',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='book',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='book',
            name='translators',
            field=models.ManyToManyField(blank=True, related_name='translated_book_set', related_query_name='translated_book', to='catalogue.Author'),
        ),
        migrations.AddField(
            model_name='book',
            name='wikidata',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='book',
            name='authors',
            field=models.ManyToManyField(blank=True, to='catalogue.Author'),
        ),
    ]

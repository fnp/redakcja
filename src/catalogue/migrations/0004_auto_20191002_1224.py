# This file is part of FNP-Redakcja, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See NOTICE for more information.
#
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0003_chunk__new_publishable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='parent',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='catalogue.Book', verbose_name='parent'),
        ),
        migrations.AlterField(
            model_name='book',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.Project'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_chunk', to=settings.AUTH_USER_MODEL, verbose_name='creator'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='head',
            field=models.ForeignKey(blank=True, default=None, editable=False, help_text="This document's current head.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.ChunkChange', verbose_name='head'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Work assignment.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='chunkchange',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='chunkchange',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='chunkchange',
            name='merge_parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='merge_children', to='catalogue.ChunkChange', verbose_name='merge parent'),
        ),
        migrations.AlterField(
            model_name='chunkchange',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='catalogue.ChunkChange', verbose_name='parent'),
        ),
        migrations.AlterField(
            model_name='image',
            name='creator',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_image', to=settings.AUTH_USER_MODEL, verbose_name='creator'),
        ),
        migrations.AlterField(
            model_name='image',
            name='head',
            field=models.ForeignKey(blank=True, default=None, editable=False, help_text="This document's current head.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.ImageChange', verbose_name='head'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.FileField(upload_to='catalogue/images', verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='image',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalogue.Project'),
        ),
        migrations.AlterField(
            model_name='image',
            name='user',
            field=models.ForeignKey(blank=True, help_text='Work assignment.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='imagechange',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='imagechange',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='imagechange',
            name='merge_parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='merge_children', to='catalogue.ImageChange', verbose_name='merge parent'),
        ),
        migrations.AlterField(
            model_name='imagechange',
            name='parent',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='catalogue.ImageChange', verbose_name='parent'),
        ),
    ]

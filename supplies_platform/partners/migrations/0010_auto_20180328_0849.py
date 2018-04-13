# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-03-28 08:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0009_auto_20180328_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pca',
            name='initiation_date',
            field=models.DateField(blank=True, help_text='The date the partner submitted complete partnership documents to Unicef', null=True, verbose_name='Submission Date'),
        ),
        migrations.AlterField(
            model_name='pca',
            name='unicef_managers',
            field=models.ManyToManyField(blank=True, null=True, to=settings.AUTH_USER_MODEL, verbose_name='Unicef focal points'),
        ),
    ]
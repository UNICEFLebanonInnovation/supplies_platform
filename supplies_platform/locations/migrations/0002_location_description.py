# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-10 06:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='description',
            field=models.CharField(default=None, max_length=254),
            preserve_default=False,
        ),
    ]

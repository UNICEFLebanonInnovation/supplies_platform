# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-14 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20180414_1855'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='p_code',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]

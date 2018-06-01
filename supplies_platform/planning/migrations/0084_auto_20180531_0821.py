# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-31 08:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0008_auto_20180426_1310'),
        ('planning', '0083_auto_20180530_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplan',
            name='items',
            field=models.ManyToManyField(blank=True, to='supplies.SupplyItem'),
        ),
        migrations.AddField(
            model_name='supplyplan',
            name='wave_number',
            field=models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], null=True),
        ),
    ]
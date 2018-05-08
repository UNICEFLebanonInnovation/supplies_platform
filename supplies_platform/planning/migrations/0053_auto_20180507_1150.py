# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-07 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0052_auto_20180507_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributionplan',
            name='to_delivery',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='distributionplanitemreceived',
            name='quantity_requested',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

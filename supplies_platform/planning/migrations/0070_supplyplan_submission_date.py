# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-19 21:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0069_auto_20180518_2244'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplan',
            name='submission_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

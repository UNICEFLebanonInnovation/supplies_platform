# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-27 21:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backends', '0007_auto_20180519_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-10 06:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0016_auto_20180409_0946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplyplan',
            name='partnership',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Reference number'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-03 13:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0094_auto_20180603_1235'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributeditemsite',
            name='distribution_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='distributeditemsite',
            name='quantity_distributed_per_site',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-08 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0007_auto_20170908_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releaseorder',
            name='unloading_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-04 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transport', '0003_auto_20170703_1238'),
    ]

    operations = [
        migrations.AddField(
            model_name='transportdetail',
            name='sub_waybill_ref',
            field=models.CharField(blank=True, max_length=256L, null=True),
        ),
    ]
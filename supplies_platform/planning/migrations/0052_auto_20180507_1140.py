# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-07 11:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0008_auto_20180426_1310'),
        ('planning', '0051_auto_20180507_1124'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='distributionplanitemreceived',
            name='date_distributed',
        ),
        migrations.RemoveField(
            model_name='distributionplanitemreceived',
            name='quantity_distributed',
        ),
        migrations.RemoveField(
            model_name='distributionplanitemreceived',
            name='wave',
        ),
        migrations.RemoveField(
            model_name='distributionplanitemreceived',
            name='wave_number',
        ),
        migrations.AddField(
            model_name='distributionplanitemreceived',
            name='supply_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_items', to='supplies.SupplyItem'),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-06 15:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0045_auto_20180506_1048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributeditem',
            name='supply_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributed_items', to='supplies.SupplyItem'),
        ),
    ]
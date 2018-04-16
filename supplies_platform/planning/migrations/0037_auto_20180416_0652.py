# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-16 06:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0036_distributionplanwave_delivery_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributionplanwave',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supply_waves', to='planning.DistributionPlanItem'),
        ),
        migrations.AlterField(
            model_name='distributionplanwave',
            name='supply_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supply_items', to='supplies.SupplyItem'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-04-14 21:19
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0005_location_p_code'),
        ('planning', '0035_auto_20180414_2105'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributionplanwave',
            name='delivery_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='item_delivery_location', to='locations.Location'),
        ),
    ]
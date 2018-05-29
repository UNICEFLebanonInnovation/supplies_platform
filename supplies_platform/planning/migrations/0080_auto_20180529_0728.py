# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-29 07:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0079_auto_20180529_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributeditem',
            name='wave',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='distributed_wave', to='planning.DistributionPlanItem'),
        ),
        migrations.AlterField(
            model_name='distributionplanitemreceived',
            name='wave',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='received_wave', to='planning.DistributionPlanItem'),
        ),
    ]

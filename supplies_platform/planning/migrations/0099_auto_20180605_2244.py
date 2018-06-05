# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-06-05 22:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0098_supplyplanwaveitem_plan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributionplan',
            name='status',
            field=models.CharField(choices=[('planned', 'Planned'), ('submitted', 'Submitted/Plan completed'), ('reviewed', 'Reviewed'), ('cleared', 'Cleared'), ('approved', 'Approved'), ('cancelled', 'Cancelled')], default='planned', max_length=32),
        ),
    ]

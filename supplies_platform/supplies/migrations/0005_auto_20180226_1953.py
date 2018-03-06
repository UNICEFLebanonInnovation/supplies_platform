# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-26 19:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0004_remove_supplyitem_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplyitem',
            name='quantity_in_stock',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supplyitem',
            name='unit_of_measure',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='supplyitem',
            name='unit_volume',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='M3', max_digits=3, null=True),
        ),
        migrations.AlterField(
            model_name='supplyitem',
            name='unit_weight',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='KG', max_digits=3, null=True),
        ),
    ]

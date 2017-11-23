# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-15 16:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0001_initial'),
        ('supplies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='Quantity required for this location')),
                ('date_required_by', models.DateField()),
                ('date_distributed_by', models.DateField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplies.SupplyItem')),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='locations.Location')),
            ],
        ),
        migrations.CreateModel(
            name='SupplyPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(help_text='PD Quantity')),
                ('target_population', models.IntegerField(help_text='No. of beneficiaries')),
                ('covered_per_item', models.IntegerField(help_text='Beneficiaries covered per item')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='supplies.SupplyItem')),
            ],
        ),
        migrations.AddField(
            model_name='distributionplan',
            name='supply_plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.SupplyPlan'),
        ),
    ]

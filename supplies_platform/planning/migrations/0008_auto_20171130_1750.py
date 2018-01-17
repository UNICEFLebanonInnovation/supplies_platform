# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-30 17:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0007_wave_wave_number'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Wave',
            new_name='WavePlan',
        ),
        migrations.DeleteModel(
            name='DistributionPlanItem',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='contact_person',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='date_distributed_by',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='date_required_by',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='delivery_location',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='purpose',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='quantity_requested',
        ),
        migrations.RemoveField(
            model_name='supplyplanitem',
            name='site',
        ),
        migrations.CreateModel(
            name='DistributionPlanItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_requested', models.PositiveIntegerField(blank=True, help_text='Quantity required for this location', null=True)),
                ('date_required_by', models.DateField(blank=True, null=True)),
                ('date_distributed_by', models.DateField(blank=True, null=True)),
                ('contact_person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('delivery_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supply_items', to='locations.Location')),
                ('site', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='locations.Location')),
                ('wave', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.WavePlan')),
            ],
        ),
    ]

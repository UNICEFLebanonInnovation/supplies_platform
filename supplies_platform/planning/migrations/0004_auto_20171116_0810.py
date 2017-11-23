# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-11-16 08:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0003_auto_20171115_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplanitem',
            name='contact_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supplyplanitem',
            name='delivery_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supply_items', to='locations.Location'),
        ),
        migrations.AddField(
            model_name='supplyplanitem',
            name='purpose',
            field=models.CharField(blank=True, choices=[('emergency_request', 'Emergency Request'), ('pd_request', 'PD Request')], max_length=50, null=True),
        ),
    ]
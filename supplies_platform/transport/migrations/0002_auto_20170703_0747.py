# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-03 07:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('transport', '0001_initial'),
        ('locations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='transportdetail',
            name='focal_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Focal Point+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transportdetail',
            name='loading_warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loading warehouse+', to='transport.Warehouse'),
        ),
        migrations.AddField(
            model_name='transportdetail',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='locations.Location'),
        ),
        migrations.AddField(
            model_name='transportdetail',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transport.Section'),
        ),
        migrations.AddField(
            model_name='transportdetail',
            name='transporter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Transporter Company+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='item',
            name='transport_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transport.TransportDetail'),
        ),
    ]

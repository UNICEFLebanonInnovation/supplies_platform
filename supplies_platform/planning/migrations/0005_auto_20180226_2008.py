# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-26 20:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0004_auto_20180226_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplan',
            name='approval_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplyplan',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supplyplan',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
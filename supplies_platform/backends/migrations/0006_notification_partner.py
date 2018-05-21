# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-19 20:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0012_auto_20180412_1315'),
        ('backends', '0005_notification_send_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='partner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='partners.PartnerOrganization'),
        ),
    ]
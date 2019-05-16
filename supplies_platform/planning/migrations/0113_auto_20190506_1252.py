# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2019-05-06 12:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('supplies', '0013_grant'),
        ('planning', '0112_auto_20190503_1058'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplanitem',
            name='activity_reference',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='supplyplanitem',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplyplanitem',
            name='grant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supplies.Grant'),
        ),
        migrations.AddField(
            model_name='supplyplanitem',
            name='solicitation_method',
            field=models.CharField(blank=True, choices=[('Low Value', 'Low Value'), ('Request for Quotation (RFQ)', 'Request for Quotation (RFQ)'), ('Invitation To Bid (ITB)', 'Invitation To Bid (ITB)'), ('Request for Proposal (RFP)', 'Request for Proposal (RFP)'), ('Long Term Agreement (LTA)', 'Long Term Agreement (LTA)'), ('Direct Order', 'Direct Order'), ('Off shore (SD)', 'Off shore (SD)')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='supplyplanservice',
            name='activity_reference',
            field=models.CharField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='supplyplanservice',
            name='expiry_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='supplyplanservice',
            name='grant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='supplies.Grant'),
        ),
        migrations.AddField(
            model_name='supplyplanservice',
            name='solicitation_method',
            field=models.CharField(blank=True, choices=[('Low Value', 'Low Value'), ('Request for Quotation (RFQ)', 'Request for Quotation (RFQ)'), ('Invitation To Bid (ITB)', 'Invitation To Bid (ITB)'), ('Request for Proposal (RFP)', 'Request for Proposal (RFP)'), ('Long Term Agreement (LTA)', 'Long Term Agreement (LTA)'), ('Direct Order', 'Direct Order'), ('Off shore (SD)', 'Off shore (SD)')], max_length=32, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-05-08 11:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0006_auto_20180417_0752'),
        ('planning', '0053_auto_20180507_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributedItemSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_distributed_per_site', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='distributeditem',
            name='site',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='locations.Location'),
        ),
        migrations.AlterField(
            model_name='distributionplan',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('planned', 'Planned'), ('submitted', 'Submitted/Plan completed'), ('reviewed', 'Reviewed'), ('cleared', 'Cleared'), ('approved', 'Approved'), ('completed', 'Distribution Completed'), ('cancelled', 'Cancelled')], default='draft', max_length=32),
        ),
        migrations.AddField(
            model_name='distributeditemsite',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='distributed_sites', to='planning.DistributedItem'),
        ),
        migrations.AddField(
            model_name='distributeditemsite',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.Location'),
        ),
    ]

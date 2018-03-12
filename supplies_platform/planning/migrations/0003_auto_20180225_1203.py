# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2018-02-25 12:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('planning', '0002_auto_20180225_1203'),
        ('locations', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplyplan',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Section'),
        ),
        migrations.AddField(
            model_name='distributionplanitem',
            name='contact_person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='distributionplanitem',
            name='delivery_location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supply_items', to='locations.Location'),
        ),
        migrations.AddField(
            model_name='distributionplanitem',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.DistributionPlan'),
        ),
        migrations.AddField(
            model_name='distributionplanitem',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='locations.Location'),
        ),
        migrations.AddField(
            model_name='distributionplanitem',
            name='wave',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.WavePlan'),
        ),
        migrations.AddField(
            model_name='distributionplan',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.SupplyPlan'),
        ),
        migrations.AddField(
            model_name='distributionitemrequest',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='distributionitemrequest',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planning.DistributionPlan'),
        ),
        migrations.AddField(
            model_name='distributionitemrequest',
            name='requested_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='distributionitemrequest',
            name='reviewed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='distributionitemrequest',
            name='validated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
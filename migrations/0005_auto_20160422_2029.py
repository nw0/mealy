# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-22 20:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mealy', '0004_auto_20160411_1532'),
    ]

    operations = [
        migrations.CreateModel(
            name='Standard_Inst',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inst_name', models.CharField(max_length=40)),
                ('usual_price', models.FloatField()),
                ('use_formal', models.BooleanField(default=False)),
                ('orig_units', models.CharField(max_length=6)),
                ('orig_amt', models.FloatField()),
            ],
            options={
                'verbose_name': 'standard resource instance',
            },
        ),
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name_plural': 'dishes'},
        ),
        migrations.AlterModelOptions(
            name='resource_inst',
            options={'verbose_name': 'resource instance'},
        ),
        migrations.AlterModelOptions(
            name='resource_ticket',
            options={'verbose_name': 'resource ticket'},
        ),
        migrations.AlterModelOptions(
            name='resource_type',
            options={'verbose_name': 'resource type'},
        ),
        migrations.AddField(
            model_name='standard_inst',
            name='inst_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mealy.Resource_Type'),
        ),
    ]

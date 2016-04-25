# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-25 16:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mealy', '0006_auto_20160423_1949'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shortcode', models.CharField(max_length=8)),
                ('verbose_name', models.CharField(max_length=20)),
                ('verbose_plural', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='resource_inst',
            name='orig_unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mealy.Unit'),
        ),
    ]
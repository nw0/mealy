# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-09 20:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mealy', '0002_auto_20160322_1117'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dish',
            name='open_cost',
        ),
        migrations.RemoveField(
            model_name='meal',
            name='dish_deps',
        ),
        migrations.RemoveField(
            model_name='meal',
            name='meal_cost',
        ),
    ]
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cooking_style', models.CharField(max_length=8, choices=[(b'frying', b'Fried'), (b'boiling', b'Boiled'), (b'instant', b'Microwaved')])),
                ('ticket_deps', models.IntegerField(default=0)),
                ('open_cost', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cons_time', models.DateTimeField(verbose_name=b'time eaten')),
                ('meal_type', models.CharField(max_length=10, choices=[(b'Breakfast', b'Breakfast'), (b'Lunch', b'Lunch'), (b'Dinner', b'Dinner'), (b'Tea', b'Tea'), (b'Supper', b'Supper'), (b'Snack', b'Snack')])),
                ('meal_cost', models.FloatField(default=0)),
                ('dish_deps', models.IntegerField(default=0)),
                ('meal_owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resource_Inst',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('res_name', models.CharField(max_length=40)),
                ('unit_use_formal', models.BooleanField(default=False)),
                ('units_original', models.CharField(max_length=6)),
                ('amt_original', models.IntegerField()),
                ('price', models.IntegerField()),
                ('used_so_far', models.FloatField(default=0)),
                ('best_before', models.BooleanField(default=False)),
                ('best_bef_date', models.DateTimeField(verbose_name=b'best before date')),
                ('purchase_date', models.DateTimeField(verbose_name=b'purchase date')),
                ('exhausted', models.BooleanField(default=False)),
                ('last_mod', models.DateTimeField(auto_now=True)),
                ('inst_owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Resource_Ticket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('used_on_ticket', models.FloatField()),
                ('ticket_cost', models.FloatField()),
                ('finalised', models.BooleanField(default=False)),
                ('par_dish', models.ForeignKey(to='mealy.Dish')),
                ('resource_inst', models.ForeignKey(to='mealy.Resource_Inst')),
            ],
        ),
        migrations.CreateModel(
            name='Resource_Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('r_name', models.CharField(max_length=40)),
                ('r_parent', models.ForeignKey(default=None, to='mealy.Resource_Type', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='resource_inst',
            name='res_type',
            field=models.ForeignKey(to='mealy.Resource_Type'),
        ),
        migrations.AddField(
            model_name='dish',
            name='par_meal',
            field=models.ForeignKey(to='mealy.Meal'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-18 23:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hello', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=120)),
                ('name', models.CharField(default=b'Anonymous', max_length=120)),
                ('message', models.TextField()),
            ],
        ),
    ]

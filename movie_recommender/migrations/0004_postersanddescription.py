# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-01-04 18:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie_recommender', '0003_titles_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostersAndDescription',
            fields=[
                ('movie_id', models.TextField(blank=True, primary_key=True, serialize=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('image_url', models.TextField(blank=True, null=True)),
            ],
        ),
    ]

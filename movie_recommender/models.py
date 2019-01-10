# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Titles(models.Model):
    movie_id = models.TextField(blank=True, primary_key=True)
    movie_title = models.TextField(blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    genres = models.TextField(blank=True, null=True)
    actors = models.TextField(blank=True, null=True)
    writers = models.TextField(blank=True, null=True)
    producers = models.TextField(blank=True, null=True)
    cinematographer = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)

class Sim_scores(models.Model):
    movie_id = models.TextField(default=None, primary_key=True)
    scores = models.TextField()


class Ratings(models.Model):
    user = models.IntegerField(default=None, primary_key=True)
    ratings = models.TextField()
    average_rating = models.DecimalField(default=None, max_digits=4, decimal_places=3)

class UpdateDB(models.Model):
    update_number = models.IntegerField(primary_key=True)
    titles_lines_to_skip = models.BigIntegerField()
    professions_lines_to_skip = models.BigIntegerField()

class PostersAndDescription(models.Model):
    movie_id = models.TextField(blank=True, primary_key=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.TextField(blank=True, null=True)
from django.test import TestCase
from django.urls import reverse
from ..tasks import *
from movie_recommender.models import Titles, Ratings
import json
import random

class ModelTests(TestCase):
    def setUp(self):
        Titles.objects.create(movie_id="1",movie_title="Hello", year=1980,
                                genres=json.dumps(["Fantasy","Action"]), actors=json.dumps(["actor1","actor2"]),
                                writers=json.dumps(['writer1',"writer2"]), producers=json.dumps(["producer1"]),
                                cinematographer=json.dumps(["cinematographer1"]), director=json.dumps(["director1"])).save()
        Titles.objects.create(movie_id="2",movie_title="Hello2", year=1977, 
                                genres=json.dumps(["Drama"]), actors=json.dumps(["actor4","actor6"]),
                                writers=json.dumps(['writer3',"writer10"]), producers=json.dumps(["producer2"]),
                                cinematographer=json.dumps(["cinematographer2"]), director=json.dumps(["director2"])).save()
        Titles.objects.create(movie_id="3",movie_title="Hello3", year=1997, 
                                genres=json.dumps(["Drama","Suspense"]), actors=json.dumps(["actor1","actor6"]),
                                writers=json.dumps(['writer1',"writer2"]), producers=json.dumps(["producer1"]),
                                cinematographer=json.dumps(["cinematographer2"]), director=json.dumps(["director1"])).save()
        Titles.objects.create(movie_id="4",movie_title="Hello4", year=2008, 
                                genres=json.dumps(["Fantasy","Adventure","Drama"]), actors=json.dumps(["actor4","actor6"]),
                                writers=json.dumps(['writer2',"writer4"]), producers=json.dumps(["producer2"]),
                                cinematographer=json.dumps(["cinematographer1"]), director=json.dumps(["director1"])).save()
        Titles.objects.create(movie_id="5",movie_title="Hello5", year=2014, 
                                genres=json.dumps(["Documentary","Drama","Action"]), actors=json.dumps(["actor2","actor6"]),
                                writers=json.dumps(['writer10',"writer3"]), producers=json.dumps(["producer3"]),
                                cinematographer=json.dumps(["cinematographer1"]), director=json.dumps(["director1"])).save()
        Titles.objects.create(movie_id="6",movie_title="Hello6", year=1952, 
                                genres=json.dumps(["Horror","Adventure"]), actors=json.dumps(["actor1","actor2"]),
                                writers=json.dumps(['writer1',"writer2"]), producers=json.dumps(["producer1"]),
                                cinematographer=json.dumps(["cinematographer1"]), director=json.dumps(["director1"])).save()
        Titles.objects.create(movie_id="7",movie_title="Hello7", year=1952, 
                                genres=json.dumps(["Horror","Adventure","Fantasy"]), actors=json.dumps(["actor4","actor2"]),
                                writers=json.dumps(['writer1',"writer4"]), producers=json.dumps(["producer3"]),
                                cinematographer=json.dumps(["cinematographer4"]), director=json.dumps(["director4"])).save()
        Titles.objects.create(movie_id="8",movie_title="Hello8", year=1952, 
                                genres=json.dumps(["Horror","Adventure","Fantasy"]), actors=json.dumps(["actor4","actor2"]),
                                writers=json.dumps(['writer1',"writer4"]), producers=json.dumps(["producer3"]),
                                cinematographer=json.dumps(["cinematographer4"]), director=json.dumps(["director4"])).save()
        Titles.objects.create(movie_id="9",movie_title="Hello9", year=1952, 
                                genres=json.dumps(["Horror","Adventure","Fantasy"]), actors=json.dumps(["actor4","actor2"]),
                                writers=json.dumps(['writer1',"writer4"]), producers=json.dumps(["producer3"]),
                                cinematographer=json.dumps(["cinematographer4"]), director=json.dumps(["director4"])).save()

        Ratings.objects.create(user='1', ratings=json.dumps({'1':4, '2':3, '5':4}), average_rating = 11.0/3.0).save()
        Ratings.objects.create(user='2', ratings=json.dumps({'1':3, '2':5, '3':5}), average_rating = 13.0/3.0).save()
        Ratings.objects.create(user='3', ratings=json.dumps({'2':5, '4':2, '6':2, '7':5}), average_rating = 14.0/4.0).save()
        Ratings.objects.create(user='4', ratings=json.dumps({'1':1, '3':5, '7':2}), average_rating = 8.0/3.0).save()
        Ratings.objects.create(user='5', ratings=json.dumps({'1':2, '2':4, '3':3}), average_rating = 9.0/3.0).save()

    given_ratings = {'1':4, '2':5}

    def test_get_movies_helper_movie_sim(self):
        recommendations = get_movies_helper(self.given_ratings)
        self.assertEqual(recommendations['6'][3], 1)

    def test_get_movies_helper_cbf(self):
        for i in range(6,15000):
            num_movies = random.randint(1,3)
            ratings = {}
            avg_rating = 0
            for j in range(0,num_movies):
                random_movie = random.randint(1,7)
                random_rating = random.randint(1,5)
                ratings[str(random_movie)] = random_rating
                avg_rating += random_rating
            avg_rating = avg_rating/float(num_movies)
            Ratings.objects.create(user=str(i), ratings = json.dumps(ratings), average_rating = avg_rating).save()

        recommendations = get_movies_helper(self.given_ratings)
        self.assertIsNotNone(recommendations)
        self.assertEqual(len(recommendations), 5)

    def test_get_movies_helper_cbf_no_sim_users(self):      
        new_ratings = {'8':2, '9':4}
        recommendations = get_movies_helper(new_ratings)
        self.assertEqual(len(recommendations), 5)
        self.assertNotEqual(recommendations, None)
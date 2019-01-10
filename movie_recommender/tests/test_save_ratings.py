from django.test import TestCase
from django.urls import reverse
from movie_recommender.models import *
import json

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




	def test_wrong_method(self):
		response = self.client.get(reverse('save_ratings'))
		self.assertEqual(response.status_code, 405)

	def test_saved_ratings(self):
		response = self.client.post(reverse('get_recommendations'), {'1':4})
		response2 = self.client.head(reverse('save_ratings'))

		query_response =  Ratings.objects.all().values()[0]
		average_rating = query_response['average_rating']
		user_id = query_response['user']
		ratings = query_response['ratings']
		
		self.assertEqual(user_id,1)
		self.assertEqual(average_rating,4.0)
		self.assertEqual(ratings, json.dumps({'1':4}))

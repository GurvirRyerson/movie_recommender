from django.test import TestCase
from django.urls import reverse
from ..recommender_system import *
from movie_recommender.models import Titles, Ratings
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

		Ratings.objects.create(user='1', ratings=json.dumps({'tt1':4, 'tt2':3, 'tt5':4}), average_rating = 11.0/3.0).save()
		Ratings.objects.create(user='2', ratings=json.dumps({'tt1':3, 'tt2':5, 'tt3':5}), average_rating = 13.0/3.0).save()
		Ratings.objects.create(user='3', ratings=json.dumps({'tt2':5, 'tt4':2, 'tt6':2, 'tt7':5}), average_rating = 14.0/4.0).save()
		Ratings.objects.create(user='4', ratings=json.dumps({'tt1':1, 'tt3':5, 'tt7':2}), average_rating = 8.0/3.0).save()
		Ratings.objects.create(user='5', ratings=json.dumps({'tt1':2, 'tt2':4, 'tt3':3}), average_rating = 9.0/3.0).save()

	def test_sim_score(self):
		movie_entry = Titles.objects.filter(movie_id='1').values('genres','actors','writers','producers','cinematographer','director')[0] 
		rows = Titles.objects.all()
		scores = []
		for i in rows.iterator(chunk_size=10000):
			if i.movie_id != '1':
				to_compare = {'genres':i.genres, 'actors':i.actors, 'writers':i.writers, 'producers':i.producers, 'cinematographer':i.cinematographer, 'director':i.director}
				similarity_score = compute_sim(movie_entry,to_compare)
				scores.append([i.movie_id,i.movie_title,similarity_score])

		scores = sorted(scores, key=lambda x: x[2], reverse=True)
		self.assertEqual(scores[0][0], '6')

	def test_pearson_score(self):
		user1 = {'movie1':4, 'movie2':3, 'movie3':4, 'movie4':2, 'movie5':1, 'movie8':5, 'movie10':3}
		user2 = {'movie1':2, 'movie3':4, 'movie6':4, 'movie9':3, 'movie10':3}
		user3 = {'movie2':3, 'movie4':1, 'movie5':2, 'movie6':2, 'movie9':4}
		user4 = {'movie1':4, 'movie2':3, 'movie3':4, 'movie4':2, 'movie5':1, 'movie8':5, 'movie10':3}

		other_users = {'user2':user2, 'user3':user3, 'user4':user4}
		average_ratings = {}
		average_ratings['user1'] = sum(int(user1[key]) for key in user1)/float(len(user1))  
		#Computing average ratings for users
		for user in other_users:
			user_dict = other_users[user]
			avg_rating = sum(int(user_dict[key]) for key in user_dict)/float(len(user_dict))
			average_ratings[user] = avg_rating

		ratings1 = {}
		ratings2 = {}
		pearson_sim_scores = []

		for user in other_users:
			user_dict = other_users[user]
			for i in user_dict:
				if i in user1:
					ratings1[i] = user1[i]
					ratings2[i] = user_dict[i]
			score = pearson_score(ratings1,ratings2, average_ratings['user1'], average_ratings[user])
			pearson_sim_scores.append([user, score])

		pearson_sim_scores = sorted(pearson_sim_scores, key=lambda x: x[1], reverse=True)
		self.assertEqual(pearson_sim_scores[0][0], 'user4')

	def test_cbf_correct_top_result(self):
		current_ratings = {'tt1':2, 'tt2':4}
		reccomendations = user_based_cf(current_ratings, Ratings.objects.values())
		self.assertEqual(reccomendations[0][0],'tt3')

	def test_cbf_remove_watched_movies(self):
		current_ratings = {'tt1':2, 'tt2':4, 'tt3':1}
		reccomendations = user_based_cf(current_ratings, Ratings.objects.values())
		self.assertEqual(reccomendations[0][0],'tt7')

	def test_cbf_no_sim_users(self):
		current_ratings = {'tt20':2, 'tt21':4}
		reccomendations = user_based_cf(current_ratings, Ratings.objects.values())
		self.assertEqual(reccomendations, None)


from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
import json
import sys
from movie_recommender.recommender_system import * 
from movie_recommender.models import Titles, Sim_scores, Ratings, PostersAndDescription
from django.contrib.sessions.models import Session
import random
import time


def index(request):
	response = render(request,'index.html')
	return response

#Debating on adding a timer here to limit requests
def get_titles(request):
	all_entries = Titles.objects.values('movie_title','movie_id').order_by('movie_title')
	if request.method == 'POST':
		try:
			to_query = request.POST["currently_typed"]
		except KeyError:
			return HttpResponse(status=400)
		if len(to_query) == 0: 
			return HttpResponse(status=204)
		#First query or it's a new query
		elif "previous_query" not in request.session.keys() or request.session['previous_query'] != to_query:
			content = Titles.objects.filter(movie_title__contains=to_query).values('movie_title',"movie_id", "year")[:100]
			if (len(content) == 0):
				return HttpResponse(status=204)
			response = JsonResponse(list(content), safe=False)
			request.session['previous_query'] = to_query
			return response
		else:
			return HttpResponse(status=204)

	else:
		return HttpResponse(status=405)


#Rename to post?
#Problem -> If the user disconnects before the the return, the session variable is set to false for quite a while
def get_movies(request):
	if request.method == "POST":
		if "processing_request" not in request.session:
			request.session['processing_request'] = False

		if request.session['processing_request'] == False:
			request.session['processing_request'] = True
			request.session.save()

			movies_ratings_dict = {}
			for key in request.POST:
				if Titles.objects.filter(movie_id=key).exists():
					movies_ratings_dict[key] = int(request.POST[key])


			if len(movies_ratings_dict) == 0:
				request.session['processing_request'] = False
				request.session.save()
				return HttpResponse(status=400)

			request.session['ratings'] = movies_ratings_dict
			movie_titles = get_movies_helper(movies_ratings_dict)

			request.session['processing_request'] = False
			request.session.save()

			return JsonResponse(movie_titles, safe=False)
		else:
			return HttpResponse(status=409)
	else:
		return HttpResponse(status=405)
		
def get_movies_helper(movies_ratings_dict):	
	if (Ratings.objects.all().count() > 10000): #Change this to use count() instead of length
		to_watch_list =  user_based_cf(movies_ratings_dict, Ratings.objects.values())
		to_watch_dict = {}
		for i in to_watch_list:
			to_watch_dict[i[0]] = Titles.objects.get(movie_id=i[0]).movie_title
		return to_watch_dict
	else:
		rows = Titles.objects.values() 
		movies = []
		scores_all = []
		#Maybe look into parallelizing this 
		for movie_id in movies_ratings_dict:
			movies.append(movie_id)
			try:
				scores = Sim_scores.objects.get(movie_id=movie_id).scores
				scores = json.loads(scores)
				scores_all.append(scores)
				continue
			except ObjectDoesNotExist:
				scores = []
			try:
				movie_entry = Titles.objects.filter(movie_id=movie_id).values()[0] 
			except IndexError:
				print ("No movie in the db with that id")

			#parallelize for speed up
			for i in rows:
				if i['movie_id'] != movie_id:
					scores.append([i['movie_id'],i['movie_title'],compute_sim(movie_entry,i)])
			scores = sorted(scores, key=lambda x: x[2], reverse=True)[0:5]


			sim_score = Sim_scores(movie_id = movie_id, scores = json.dumps(scores))
			if (Sim_scores.objects.filter(movie_id = movie_id).exists() == False):
				sim_score.save()

			scores_all.append(scores)
		top_5 = {}
		scores_all = sorted([item for sublist in scores_all for item in sublist], key=lambda x: x[2], reverse=True)
		#i[0] is movie_id, i[1] is movie_title
		rank = 1
		for i in scores_all:
			if i[1] not in movies:
				if PostersAndDescription.objects.filter(movie_id=i[0]).exists():
					x = PostersAndDescription.objects.filter(movie_id=i[0])[0]
					poster_path = x.image_url
					description = x.description
				else:
					poster_path = None
					description = None
				top_5[i[0]] = [i[1],poster_path,description,rank]
				rank += 1
			if len(top_5) == 5:
				return top_5

		return top_5
		
def save_ratings(request):
	if request.method == "HEAD":
		if "ratings" in request.session:
			ratings = request.session['ratings']
			avg_rating = 0
			for movie_id in ratings:
				avg_rating += int(ratings[movie_id])

			#Could also use some other selecting user ids, like using the session id. Don't know if that is unique or not
			try:
				latest_user = Ratings.objects.latest('user').user 
				User_id = latest_user + 1
			except ObjectDoesNotExist:
				user_id = 1

			ratings_to_insert = Ratings(user=user_id, ratings=json.dumps(ratings), average_rating = float(avg_rating)/len(ratings))
			ratings_to_insert.save()
			return HttpResponse(status=200)
	else:
		return HttpResponse(status=405)
'''
def test_cbf(request):
	if request.method == "POST":
		movies_ratings_dict = {}
		for key in request.POST:
			movies_ratings_dict[key] = int(request.POST[key])

		if len(movies_ratings_dict) == 0:
			return JsonResponse({},safe=False)

		rows = Titles.objects.values('movie_id')
		print rows[0]
		row_len = len(rows)
		test_ratings = []
		for i in range(1,500000):
			test_user_ratings_dict = {}
			average_rating = 0
			for j in range(1, random.randint(5,8)):
				rand_row = random.randint(0,row_len-1)
				rating = random.randint(1,5)
				test_user_ratings_dict[rows[rand_row]['movie_id']] = rating
				average_rating += rating

			test_user_ratings_list = {'user':i, 'ratings':json.dumps(test_user_ratings_dict), 'average_rating':float(average_rating)/len(test_user_ratings_dict)}
			test_ratings.append(test_user_ratings_list)

		to_watch_list =  user_based_cf(movies_ratings_dict, test_ratings)
		to_watch_dict = {}
		for i in to_watch_list:
			to_watch_dict[i[0]] = Titles.objects.get(movie_id=i[0]).movie_title
		print "To watch = " + json.dumps(to_watch_dict)
		return JsonResponse(to_watch_dict, safe=False)
'''







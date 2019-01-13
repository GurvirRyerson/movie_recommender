from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
from movie_recommender.recommender_system import * 
from movie_recommender.models import Titles, Sim_scores, Ratings, PostersAndDescription
from django.db.models.functions import Length
from django.contrib.sessions.models import Session
import random
import time
import json
import sys
from .tasks import get_movies_helper
from celery.result import AsyncResult
from celery.task.control import revoke
from ratelimit.decorators import ratelimit

@ensure_csrf_cookie
def index(request):
	response = render(request,'index.html')
	return response

def get_titles(request):
	if request.method == 'POST':
		try:
			to_query = request.POST["currently_typed"]
		except KeyError:
			return HttpResponse(status=400)
		if len(to_query) == 0: 
			return HttpResponse(status=204)
		#First query or it's a new query
		elif "previous_query" not in request.session.keys() or request.session['previous_query'] != to_query:
			print(to_query)
			content = Titles.objects.filter(movie_title__icontains=to_query).values('movie_title',"movie_id", "year").order_by(Length('movie_title').asc())[:50]
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
def get_movies(request):
	if request.method == "POST":
		if 'task_id' in request.session.keys():
			revoke(request.session['task_id'], terminate=True)
			print("Terminated", request.session['task_id'])
		movies_ratings_dict = {}
		for key in request.POST:
			if Titles.objects.filter(movie_id=key).exists():
				movies_ratings_dict[key] = int(request.POST[key])


		if len(movies_ratings_dict) == 0:
			return HttpResponse(status=400)

		#Put something here to kill tasks when update is called again
		request.session['ratings'] = movies_ratings_dict
		top_5_taskID = get_movies_helper.delay(movies_ratings_dict)
		request.session['task_id'] = str(top_5_taskID)
		request.session.save()
		return HttpResponse(top_5_taskID, status=200)
	else:
		return HttpResponse(status=405)

@ratelimit(block=True, key='ip', rate='1/s')
def task_done(request):
	if request.method == "GET":
		task_status = request.GET['taskID']
		res = AsyncResult(task_status)
		if res.state == 'SUCCESS':
			return JsonResponse(res.result, safe=False)
		elif res.state == 'FAILURE':
			with open("/home/gurvir/movie_recommender_project/debug_file.tx", "w") as f:
				f.write(res.result)
				f.write(res.failed())
			return HttpResponse(status=500)
		else:
			if request.GET['taskID'] != request.session['task_id']:
				return HttpResponse(status=204)
			else:
				return HttpResponse(status=202)
	else:
		return HttpResponse(status=405)


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
				user_id = latest_user + 1
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







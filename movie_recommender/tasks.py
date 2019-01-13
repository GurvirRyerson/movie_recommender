from .models import Titles, Ratings, Sim_scores, PostersAndDescription
from django.core.exceptions import ObjectDoesNotExist
from movie_recommender.recommender_system import * 

from celery.decorators import task

@task(name="get_top5_movies")
def get_movies_helper(movies_ratings_dict):	
	if (Ratings.objects.all().count() > 10000): #Change this to use count() instead of length
		to_watch_list =  user_based_cf(movies_ratings_dict, Ratings.objects.values())
		to_watch_dict = {}
		for i in to_watch_list:
			to_watch_dict[i[0]] = Titles.objects.get(movie_id=i[0]).movie_title
		return to_watch_dict
	else:
		#Not enough memory to load entire db, have to go search line by line
		rows = Titles.objects.all()
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
				movie_entry = Titles.objects.filter(movie_id=movie_id).values('genres','actors','writers','producers','cinematographer','director')[0] 
			except IndexError:
				print ("No movie in the db with that id")

			#parallelize for speed up
			for i in rows.iterator(chunk_size=10000):
				to_compare = {'genres':i.genres, 'actors':i.actors, 'writers':i.writers, 'producers':i.producers, 'cinematographer':i.cinematographer, 'director':i.director}
				if i.movie_id != movie_id:
					similarity_score = compute_sim(movie_entry,to_compare)
					if similarity_score > 0:
						scores.append([i.movie_id,i.movie_title,similarity_score])

			scores = sorted(scores, key=lambda x: x[2], reverse=True)

			sim_score = Sim_scores(movie_id = movie_id, scores = json.dumps(scores))
			if (Sim_scores.objects.filter(movie_id = movie_id).exists() == False):
				sim_score.save()

			scores_all.append(scores)
		top_5 = {}
		scores_all = sorted([item for sublist in scores_all for item in sublist], key=lambda x: x[2], reverse=True)
		#i[0] is movie_id, i[1] is movie_title
		rank = 1
		for i in scores_all:
			if len(top_5) == 5:
				return top_5
			elif i[0] not in movies and i[0] not in top_5:
				if PostersAndDescription.objects.filter(movie_id=i[0]).exists():
					x = PostersAndDescription.objects.filter(movie_id=i[0])[0]
					poster_path = x.image_url
					description = x.description
				else:
					poster_path = None
					description = None
				top_5[i[0]] = [i[1],poster_path,description,rank]
				rank += 1
			else:
				continue
		return top_5

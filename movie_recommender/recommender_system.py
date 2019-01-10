import json
import random
import time
import math

def user_based_cf(current_ratings,entries):
	avg_rating1 = sum(int(current_ratings[key]) for key in current_ratings)/len(current_ratings)
	#for i in entries:
	#	entry = json.loads(i['ratings'])

	pearson_sim_scores = []
	for i in entries:
		entry = json.loads(i['ratings'])
		avg_rating2 = float(i['average_rating'])

		ratings1 = {}
		ratings2 = {}

		for j in entry:
			if j in current_ratings:
				ratings1[j] = entry[j]
				ratings2[j] = current_ratings[j]

		if len(ratings1) > 0:
			score = pearson_score(ratings1,ratings2,avg_rating1,avg_rating2)
			pearson_sim_scores.append([i['user'],score, avg_rating2])


	pearson_sim_scores = sorted(pearson_sim_scores, key=lambda x: x[1], reverse=True)
	with open('pearson_scores.txt','w') as fp:
		for i in pearson_sim_scores:
			fp.write(json.dumps(i))
			
	k = 50
	sim_users = []
	for i in pearson_sim_scores:
		for j in entries:
			if k != 0:
				if j['user'] == i[0]:
					#[pearson score, movie_ratings, avg_rating_of_user]
					sim_users.append([i[1],json.loads(j['ratings']), i[2]])
					k -=1
			else:
				break
		if k == 0:
			break

	watched = []
	for key in current_ratings:
		watched.append(key)

	return get_recommended_movies(watched,sim_users,avg_rating1)

def pearson_score(rating1,rating2,avg_rating1,avg_rating2):
	numerator = 0
	denominator_rating1 = 0
	denominator_rating2 = 0
	for key in rating1:
		x = rating1[key] - avg_rating1
		y = rating2[key] - avg_rating2

		numerator += x*y

		denominator_rating1 += x**2
		denominator_rating2 += y**2

	denominator = math.sqrt(denominator_rating1*denominator_rating2)

	if (denominator == 0):
		return 0

	return numerator/denominator

def get_recommended_movies(watched,sim_users,avg_rating_user):
	'''
		Get top K similar users
		Find movies all K have rated, that user has not rated, compute rating for movies, recommend highest rating(s)
		Expand top K if not enough movies

	'''
	ratings = []
	not_watched = []

	for users in sim_users:
		#For movie in movie_dict
		for movie_title in users[1]:
			if movie_title not in watched and movie_title not in not_watched:
				not_watched.append(movie_title)



	k = 0.0
	for movie_to_guess_rating in not_watched:
		adjust_weighted_sum = 0

		for user in sim_users:
			avg_rating_sim = user[2]
			for movie in user[1]:
				if movie == movie_to_guess_rating:
					adjust_weighted_sum += user[0]*(user[1][movie]-avg_rating_sim)
					k += abs(user[0])

		if (k != 0):			
			k = 1/k
			adjust_weighted_sum = avg_rating_user + k*adjust_weighted_sum
			ratings.append([movie_to_guess_rating,adjust_weighted_sum])
		else:
			continue

	recommended = sorted(ratings, key=lambda x: x[1], reverse=True)
	if (len(recommended) < 10):
		return recommended
	else:
		return recommended[0:10]


def compute_sim(row1,row2):
	score = 0
	#aribitrary weights
	weights = {'movie_id':0,'movie_title':0,'year':0,'genres':1.3,'actors':1.4,'writers':1.7,'producers':1.5,'cinematographer':1.1,'director':1.6}
	for col in row1:
		if (col != 'movie_id' and col !='movie_title' and col != 'year'):
			x = json.loads(row1[col])
			y = json.loads(row2[col])
			if (len(x) == 0 or len(y) == 0):
				continue
			else:
				normalize = max(len(x),len(y))
				score += weights[col] * (len(set(x).intersection(set(y))))/normalize
		else:
			continue

	return score




from django.core.management.base import BaseCommand, CommandError
from movie_recommender.models import Titles, PostersAndDescription
import csv, time, json, requests, gzip, shutil, sys, os

MOVIEDB_API_KEY = os.environ['MOVIEDB_API_KEY']
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommender.settings")

class Command(BaseCommand):
	help =  "Gets posters from movie db"

	def genUrlFind(self, movie_id):
		return "https://api.themoviedb.org/3/find/"+movie_id+"?api_key="+ MOVIEDB_API_KEY +"&language=en-US&external_source=imdb_id"

	def genUrlGetImages(self, movie_id):
		return "https://api.themoviedb.org/3/movie/"+str(movie_id)+"/images?api_key="+MOVIEDB_API_KEY+"&language=en-US"

	def makeRequest(self, url):
		r = requests.get(url)
		if 'retry-after' in r.headers:
			time.sleep(int(r.headers['retry-after'])+1)
			r = requests.get(url)
			if r.status_code != 200:
				print r.status_code
		return r

	def handle(self, *args, **options):
		r_baseURL = requests.get("https://api.themoviedb.org/3/configuration?api_key="+MOVIEDB_API_KEY)
		if r_baseURL.status_code == 200:
			r_baseURL_json =  r_baseURL.json()
			image_base_url = r_baseURL_json['images']['secure_base_url']
			poster_size = r_baseURL_json['images']['poster_sizes'][-1]
			img_path = image_base_url+poster_size

		posters_and_images_list = [] #For bulk inserting
		num_inserts = 0
		for row in Titles.objects.all():
			if PostersAndDescription.objects.filter(movie_id=row.movie_id).exists():
				continue
			if len(posters_and_images_list) >= 900:
				num_inserts += 1
				print "Done: "+ str(num_inserts) + " inserts"
				PostersAndDescription.objects.bulk_create(posters_and_images_list)
				posters_and_images_list = []

			r_find = self.makeRequest(self.genUrlFind(row.movie_id))
			if r_find.status_code == 404:
				continue
			try:
				response_find_json = r_find.json()['movie_results'][0]
			except IndexError:
				overview = None
				poster_path = None
				posters_and_images_list.append(PostersAndDescription(movie_id=row.movie_id, description=None, image_url=None))
				continue

			overview = response_find_json['overview']
			try:
				if response_find_json['poster_path'] == None:
					r_getImage = self.makeRequest(self.genUrlGetImages(response_find_json['id']))
					if r_getImage.status_code == 404:
						poster_path = None
					else:
						try:
							response_poster_json = r_getImage.json()['posters'][0]
							if response_poster_json['file_path'] != None:
								poster_path = img_path + response_poster_json['file_path']
							else:
								poster_path = None
						except IndexError:
							poster_path = None
				else:
					poster_path = img_path + response_find_json['poster_path']
			except KeyError:
				print response_find_json
				print r_find.status_code

			posters_and_images_list.append(PostersAndDescription(movie_id=row.movie_id, description=overview, image_url=poster_path))

		if posters_and_images_list != []:
			print len(posters_and_images_list)
			PostersAndDescription.objects.bulk_create(posters_and_images_list)
			posters_and_images_list = []
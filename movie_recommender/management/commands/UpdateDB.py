from django.core.management.base import BaseCommand, CommandError
from django.db.models import Max
from movie_recommender.models import Titles, Sim_scores, UpdateDB
from movie_recommender.recommender_system import compute_sim
import csv, time, json, requests, gzip, shutil, sys, os

#Need absolute path for cronjobs
FILE_PATH = "/home/gurvir/python_code/django_movie_project/movie_recommender/"
TITLES_URL = "https://datasets.imdbws.com/title.basics.tsv.gz"
PRINCIPALS_URL = "https://datasets.imdbws.com/title.principals.tsv.gz"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movie_recommender.settings")

class Command(BaseCommand):
	help = "Updates the list of movies with new movies from IMDB"

	def recomputeSimScores(self, sim_scores, movies_to_recompute, movie_dict, previous_movie_id, title):
		for index,row in enumerate(sim_scores):
			score = compute_sim(movies_to_recompute[index],movie_dict)
			row.scores = json.loads(row.scores)
			#Check if new movies sim score is higher than lowest top5 score previously calculated
			if score > row.scores[4][2]:
				row.scores[4] = [previous_movie_id, title, score]
				new_5_scores = sorted(row.scores, key=lambda x: x[2], reverse=True)
				new_scores = Sim_scores(movie_id = row.movie_id, scores = json.dumps(new_5_scores))
				new_scores.save()
			else:
				continue

	def getNewFiles(self):
		try:
			r = requests.get(TITLES_URL)
			with open(FILE_PATH+'titles.gz', "wb") as f:
				f.write(r.content)
			r = requests.get(PRINCIPALS_URL)
			with open(FILE_PATH+'principles.gz', "wb") as f:
				f.write(r.content)

			with gzip.open(FILE_PATH+'titles.gz','rb') as f_in, open(FILE_PATH+'titles.tsv', 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)

			with gzip.open(FILE_PATH+'principles.gz','rb') as f_in, open(FILE_PATH+'principles.tsv', 'wb') as f_out:
				shutil.copyfileobj(f_in, f_out)

		except Exception as e:
			print(str(e))
			sys.exit()

	def iterateOverTitles(self, titles_reader, titles_entry_counter, professions_entry_counter, update_number):
		movies = {} #Used to figure out which ids in the titles files are movies, professions does not have that info
		first_movie_gotten = False 
		for row in titles_reader:
			if row[1] == 'movie':
				if first_movie_gotten == False:
					first_movie_id = row[0]
					first_movie_gotten = True

				title = row[2]
				genres = row[-1].split(',',-1)
				genres_processed = []
				for genre in genres:
					if genre == "\\N":
						continue
					genres_processed.append(genre)
				genres = json.dumps(genres_processed)
				try:
					year = int(row[5])
				except ValueError:
					year = -1
				movies[row[0]] = [title,genres,year]
			
			titles_entry_counter += 1

		if first_movie_gotten == False:
			#No new movies found in the updated db, so exit early
	  		new_db_update = UpdateDB(update_number=update_number+1, titles_lines_to_skip=titles_entry_counter, professions_lines_to_skip=professions_entry_counter)
	  		new_db_update.save()
	  		sys.exit()
		else:
			return first_movie_id, movies, titles_entry_counter

	def iterateOverProfessions(self, professions_reader, professions_entry_counter, movies, previous_movie_id):
		movie_dict = {'actor':[],'actress':[],'writer':[],'producer':[],'cinematographer':[],'director':[]}
		movies_to_recompute = [] 
		entries_list = []
		sim_scores = Sim_scores.objects.all()
		for row in sim_scores:
			movie_entry = Titles.objects.filter(movie_id=row.movie_id).values()[0]
			movies_to_recompute.append(movie_entry)

		for row in professions_reader:
			movie_id = row[0]
			if movie_id in movies:
				if previous_movie_id == movie_id:
					profession = row[3]
					if profession in movie_dict:
						movie_dict[profession].append(row[2])
				else:
					title,genres,year = movies[previous_movie_id]
					movie_dict['actor'] = movie_dict['actor'] + movie_dict['actress']
					movie_dict.pop('actress')
					movie_dict['genres'] = genres
					for key in movie_dict:
						movie_dict[key] = json.dumps(movie_dict[key])

					#Updating previously computed movie sim scores, if the new movies are more similar than top5 similar movies
					self.recomputeSimScores(sim_scores, movies_to_recompute, movie_dict, previous_movie_id, title)

					if len(entries_list) >= 900:
						Titles.objects.bulk_create(entries_list)
						entries_list = []
					entries_list.append(Titles(movie_id=previous_movie_id,movie_title=title,year=year,genres=movie_dict['genres'],actors=movie_dict['actor'],writers=movie_dict['writer'],producers=movie_dict['producer'],cinematographer=movie_dict['cinematographer'],director=movie_dict['director']))
					movie_dict = {'actor':[],'actress':[],'writer':[],'producer':[],'cinematographer':[],'director':[]}
					previous_movie_id = movie_id
					professions_entry_counter += 1
		#Handles last rows that were < 900
		if entries_list != []:
			Titles.objects.bulk_create(entries_list)

		return professions_entry_counter

	def handle(self, *args, **options):
		#self.getNewFiles()

		try:
			lines_to_skip = UpdateDB.objects.values().order_by('-update_number')[0]
			update_number = lines_to_skip['update_number'] 
			titles_entry_counter = lines_to_skip['titles_lines_to_skip'] #number of lines to skip processing in the movie titles file
			professions_entry_counter = lines_to_skip['professions_lines_to_skip'] #number of lines to skip processing in the professions file

		except IndexError:
			#Initial lines to skip
			update_number = 0
			titles_entry_counter = 0
			professions_entry_counter = 0

		with open(FILE_PATH+"titles.tsv") as titles, open(FILE_PATH+"principles.tsv") as professions:
			titles_reader = csv.reader(titles, delimiter='\t')
			professions_reader = csv.reader(professions, delimiter='\t')

			next(titles_reader) # skip header info
			next(professions_reader) #skiper header info

			#Skip over files that are already in the db
			for i in range(0,titles_entry_counter):
				next(titles_reader)

			for i in range(0,professions_entry_counter):
				next(professions_reader)

			first_movie_id, movies, titles_entry_counter = self.iterateOverTitles(titles_reader, titles_entry_counter, professions_entry_counter, update_number)
			professions_entry_counter = self.iterateOverProfessions(professions_reader, professions_entry_counter, movies, first_movie_id)


			new_db_update = UpdateDB(update_number=update_number+1, titles_lines_to_skip=titles_entry_counter, professions_lines_to_skip=professions_entry_counter)
			new_db_update.save()

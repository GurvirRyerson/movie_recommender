from django.test import TestCase
from django.urls import reverse
from movie_recommender.models import *
from django.db.models.functions import Length

class ModelTests(TestCase):
	def setUp(self):
		Titles.objects.create(movie_id="1",movie_title="Hello").save()
		Titles.objects.create(movie_id="2",movie_title="Hell").save()
		Titles.objects.create(movie_id="3",movie_title="He").save()
		Titles.objects.create(movie_id="4",movie_title="Heman").save()
		Titles.objects.create(movie_id="5",movie_title="great").save()
		Titles.objects.create(movie_id="6",movie_title="today").save()
		Titles.objects.create(movie_id="7",movie_title="Today").save()
		Titles.objects.create(movie_id="8",movie_title="star").save()
		Titles.objects.create(movie_id="9",movie_title="za").save()
		Titles.objects.create(movie_id="10",movie_title="crazy").save()
		Titles.objects.create(movie_id="11",movie_title="never").save()
		Titles.objects.create(movie_id="12",movie_title="ok").save()

	def test_basic_retrival(self):
		#response = self.client.get(reverse("index"))
		response = self.client.post(reverse('get_titles'), {'currently_typed':"H"})
		response = response.json()
		self.assertEqual(response[0]['movie_title'], "He")

	def test_multiple_entries(self):
		query = "H"
		response = self.client.post(reverse('get_titles'), {'currently_typed':query})
		response = response.json()
		content = Titles.objects.filter(movie_title__icontains=query).values('movie_title',"movie_id", "year").order_by(Length('movie_title').asc())[:50]	
		self.assertEqual(response,list(content))

	def test_duplicate_query(self):
		response = self.client.post(reverse('get_titles'), {'currently_typed':"H"})
		response = self.client.post(reverse('get_titles'), {'currently_typed':"H"})
		self.assertEqual(response.status_code, 204)

	def test_empty_query(self):
		response = self.client.post(reverse('get_titles'), {'currently_typed':""})
		self.assertEqual(response.status_code, 204)

	def test_no_dict(self):
		response = self.client.post(reverse('get_titles'))
		self.assertEqual(response.status_code, 400)

	def test_no_titles(self):
		query = "q"
		response = self.client.post(reverse('get_titles'), {'currently_typed':query})
		self.assertEqual(response.status_code, 204)

	def test_wrong_method(self):
		response = self.client.get(reverse('get_titles'))
		self.assertEqual(response.status_code, 405)


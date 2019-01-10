from django.test import TestCase
from django.urls import reverse
from movie_recommender.models import *

class ModelTests(TestCase):

	def test_basic(self):
		Titles.objects.create(movie_id="-1",movie_title="Hello").save()
		#response = self.client.get(reverse("index"))
		response = self.client.post(reverse('get_titles'), {'currently_typed':"H"})
		response = self.client.post(reverse('get_titles'), {'currently_typed':""})
		

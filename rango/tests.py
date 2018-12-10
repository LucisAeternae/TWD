"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".
Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from rango.models import Category
from django.urls import reverse

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class CategoryMethodTest(TestCase):
    def test_ensure_views_are_positive(self):
        """
        ensure_viwes_views_are_positive should result True for Categories
        where views are zero or positive
        """
        cat = Category(name='test', views=1, likes=0)
        cat.save()
        self.assertEqual((cat.views >= 0), True)

    def test_slug_line_creation(self):
        cat = Category(name='Random Category String')
        cat.save()
        self.assertEqual(cat.slug, 'random-category-string')

class IndexViewTests(TestCase):
    def test_index_empty_cats(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'There are no categories present')
        self.assertQuerysetEqual(response.context['categories'], [])

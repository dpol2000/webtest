from django.test import TestCase, Client
from utils import normalize

class UtilsTest(TestCase):

    def test_normalize(self):
        self.assertEqual(normalize('asd'), 'ASD')
        self.assertEqual(normalize('aSd'), 'ASD')
        self.assertEqual(normalize('ASd'), 'ASD')
        self.assertEqual(normalize('ASD'), 'ASD')
        self.assertEqual(normalize('aSD'), 'ASD')
        self.assertEqual(normalize('asd.'), 'ASD')
        self.assertEqual(normalize('ASD.'), 'ASD')
        self.assertEqual(normalize('AS.D'), 'AS.D')
        self.assertEqual(normalize('as.d'), 'AS.D')


class ViewsTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_urls(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

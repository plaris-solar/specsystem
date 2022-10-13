from django.test import TestCase

from utils.test_utils import SpecTestCase

class DataTest(SpecTestCase):

    def test_data(self):
        response = self.get_request('/env/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'Test')
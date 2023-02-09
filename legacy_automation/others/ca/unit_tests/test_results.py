__author__ = 'manoj'

import unittest
from ca.clients.results import internal_mongo_results


class MongoResultTests(unittest.TestCase):
    def test_canon_good_url(self):
        results = [{"status": "success",
                    "data": 'GREEN',
                    'url': 'http://manojk.com',
                    'competitor': 'avira'}]
        internal_mongo_results(results)

    def test_canon_error(self):
        results = [{"status": "success",
                    "data": 'GREEN',
                    'url': 'http://manojk.comasdfasdf',
                    'competitor': 'avira'}]
        internal_mongo_results(results)

    def test_no_url(self):
        results = [{"status": "success",
                    "data": 'GREEN',
                    'competitor': 'avira'}]
        internal_mongo_results(results)

    def test_no_competitor(self):
        results = [{"status": "success",
                    "data": 'GREEN',
                    'url': 'http://manojk.comasdfasdf'}]
        internal_mongo_results(results)

    def test_no_data(self):
        results = [{"status": "success",
                    'url': 'http://manojk.comasdfasdf',
                    'competitor': 'avira'}]
        internal_mongo_results(results)

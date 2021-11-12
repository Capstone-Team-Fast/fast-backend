import unittest

from neomodel import config, db

from backend import settings


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_something(self):
        self.assertEqual(sum([1, 2, 3]), 6)  # add assertion here


if __name__ == '__main__':
    unittest.main()

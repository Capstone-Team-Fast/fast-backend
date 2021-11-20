import json
import unittest

from neomodel import config, db

from backend import settings
from routing.managers import NodeParser


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_create_locations(self):
        locations = [json.dumps({
            "id": 2,
            "user": None,
            "first_name": "Jean-Luc",
            "last_name": "Picard",
            "quantity": 1,
            "phone": "124-123-4567",
            "languages": [
                {
                    "id": 1,
                    "name": "English"
                },
                {
                    "id": 2,
                    "name": "French"
                },
                {
                    "id": 8,
                    "name": "German"
                }
            ],
            "location": {
                "id": 7,
                "address": "9999 Bagel St",
                "city": "Omaha",
                "state": "NE",
                "zipcode": 68123,
                "is_center": False,
                "room_number": "123",
                "latitude": None,
                "longitude": None
            }
        })]

        expected_result = json.dumps({
            'id': 2,
            'is_center': False,
            'address': {
                'id': 7,
                'address': '9999 Bagel St',
                'city': 'Omaha',
                'state': 'NE',
                'zipcode': 68123,
                'coordinates': {
                    'latitude': None,
                    'longitude': None
                }
            },
            'demand': 1,
            'languages': [
                {'id': 1, 'language': 'English'},
                {'id': 2, 'language': 'French'},
                {'id': 8, 'language': 'German'}
            ]
        })

        customers = NodeParser.create_customers(locations)
        print(customers[0].serialize())
        print(expected_result)
        self.assertEqual(customers[0].serialize(), expected_result)
        for language in customers[0].get_languages():
            language.delete()
        customers[0].address.delete()
        customers[0].delete()

    def test_create_driver(self):
        pass


if __name__ == '__main__':
    unittest.main()

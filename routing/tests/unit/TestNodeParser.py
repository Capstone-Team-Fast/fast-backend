import json
import unittest

from neomodel import config, db

from backend import settings
from routing.managers import NodeParser
from routing.models.availability import Availability
from routing.models.language import Language


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_create_locations(self):
        locations = [json.dumps({
            'id': 2,
            'user': None,
            'first_name': 'Jean-Luc',
            'last_name': 'Picard',
            'quantity': 1,
            'phone': '124-123-4567',
            'languages': [
                {'id': 1, 'name': 'English'}, {'id': 2, 'name': 'French'}, {'id': 8, 'name': 'German'}
            ],
            'location': {
                'id': 7,
                'address': '9999 Bagel St',
                'city': 'Omaha',
                'state': 'NE',
                'zipcode': 68123,
                'is_center': False,
                'room_number': '123',
                'latitude': None,
                'longitude': None
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
                {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'}, {'id': 8, 'language': 'German'}
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
        drivers = [
            json.dumps({
                'id': 18,
                'user': None,
                'first_name': 'Ben',
                'last_name': 'Kenobi',
                'capacity': 5,
                'employee_status': 'employee',
                'duration': '3',
                'delivery_limit': None,
                'phone': '123-123-4567',
                'availability': {
                    'id': 16,
                    'sunday': True,
                    'monday': False,
                    'tuesday': True,
                    'wednesday': True,
                    'thursday': False,
                    'friday': True,
                    'saturday': False
                },
                'languages': [
                    {'id': 1, 'name': 'English'}, {'id': 2, 'name': 'French'}, {'id': 3, 'name': 'Spanish'}
                ]
            }),
            json.dumps({
                'id': 18,
                'user': None,
                'first_name': 'Ben',
                'last_name': 'Kenobi',
                'capacity': 5,
                'employee_status': 'volunteer',
                'duration': '3',
                'delivery_limit': 6,
                'phone': '123-123-4567',
                'availability': {
                    'id': 16,
                    'sunday': True,
                    'monday': False,
                    'tuesday': True,
                    'wednesday': True,
                    'thursday': False,
                    'friday': True,
                    'saturday': False
                },
                'languages': [
                    {'id': 1, 'name': 'English'}, {'id': 2, 'name': 'French'}, {'id': 3, 'name': 'Spanish'}
                ]
            })
        ]

        expected_result = [
            json.dumps({
                'id': 18,
                'first_name': 'Ben',
                'last_name': 'Kenobi',
                'capacity': 5,
                'employee_status': 'P',
                'delivery_limit': None,
                'availability': [
                    {'id': None, 'day': 'Sunday'}, {'id': None, 'day': 'Friday'}, {'id': None, 'day': 'Wednesday'},
                    {'id': None, 'day': 'Tuesday'}
                ],
                'languages': [
                    {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'}, {'id': 3, 'language': 'Spanish'}
                ]
            }),
            json.dumps({
                'id': 18,
                'first_name': 'Ben',
                'last_name': 'Kenobi',
                'capacity': 5,
                'employee_status': 'V',
                'delivery_limit': 6,
                'availability': [
                    {'id': None, 'day': 'Sunday'}, {'id': None, 'day': 'Friday'}, {'id': None, 'day': 'Wednesday'},
                    {'id': None, 'day': 'Tuesday'}
                ],
                'languages': [
                    {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'}, {'id': 3, 'language': 'Spanish'}
                ]
            })]

        drivers_node = NodeParser.create_drivers(drivers)
        for index in range(len(drivers_node)):
            driver = drivers_node[index]
            print(driver.serialize())
            print(expected_result[index])
            self.assertEqual(driver.serialize(), expected_result[index])
            driver.delete()
            print()

        for language in Language.nodes.all():
            language.delete()
        for availability in Availability.nodes.all():
            availability.delete()


if __name__ == '__main__':
    unittest.main()

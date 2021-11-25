import datetime
import json
import re
import unittest

from neomodel import config, db

from backend import settings
from routing import constant
from routing.managers import RouteManager, NodeParser
from routing.tests.unit import data


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        route_manager = RouteManager(db_connection=config.DATABASE_URL)
        self.assertIsNone(route_manager.best_assignment)
        self.assertIsNone(route_manager.objective_function_value)
        self.assertListEqual(route_manager.objective_function_values, [])

    def test_request_route_template(self):
        route_manager = RouteManager(config.DATABASE_URL)
        drivers = [json.dumps({
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
                'id': 16, 'sunday': True, 'monday': False, 'tuesday': True, 'wednesday': True, 'thursday': False,
                'friday': True, 'saturday': False
            },
            'languages': [
                {'id': 1, 'name': 'English'}, {'id': 2, 'name': 'French'}, {'id': 3, 'name': 'Spanish'}
            ]
        })]
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
            'location': {'id': 7, 'address': '9999 Bagel St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68123,
                         'is_center': False, 'room_number': '123', 'latitude': None, 'longitude': None}
        })]
        departure = json.dumps({
            'location': {
                'id': 7,
                'address': '9999 Bagel St',
                'city': 'Omaha',
                'state': 'NE',
                'zipcode': 68123,
                'is_center': False,
                'room_number': None,
                'latitude': None,
                'longitude': None
            }
        })
        response = route_manager.request_routes(departure=departure, locations=locations, drivers=drivers)
        self.assertEqual(response, route_manager.response_template())

    def test_request_route_empty_connection_string(self):
        with self.assertRaises(ValueError):
            route_manager = RouteManager(db_connection='')

    def test_request_route_invalid_connection_string(self):
        with self.assertRaises(ValueError):
            route_manager = RouteManager(db_connection='bolt://userpassword@localhost:7687')

    def test_request_route(self):
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes_test(departure='', locations=[], drivers=[])
        expected_result = json.dumps({
            'solver_status': '', 'message': '', 'description': '', 'routes': []
        })
        self.assertEqual(response, expected_result)

    def test_request_route_base_case(self):
        departure = data.departure
        customers = data.get_random_customers()
        drivers = data.get_random_drivers()

        # Create routes
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes_test(departure=departure, locations=customers, drivers=drivers)
        log_filename = f'{datetime.datetime.now().strftime(constant.DATETIME_FORMAT)}'
        log_filename = re.sub('[^a-zA-Z\d]', '', log_filename)
        log_filename = log_filename + '.json'
        with open(file=log_filename, mode='w') as file:
            json.dump(json.loads(response), file, ensure_ascii=False, indent=4)

        # Cleanup database
        # data.cleanup()

    def test_request_route_generalization(self):
        departure = data.departure
        customers = data.get_random_customers(n=2)
        drivers = data.get_random_drivers(n=4)

        # Create routes
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes_test(departure=departure, locations=customers, drivers=drivers)
        log_filename = f'{datetime.datetime.now().strftime(constant.DATETIME_FORMAT)}'
        log_filename = re.sub('[^a-zA-Z\d]', '', log_filename)
        log_filename = log_filename + '.json'
        with open(file=log_filename, mode='w') as file:
            json.dump(json.loads(response), file, ensure_ascii=False, indent=4)

        # Cleanup database
        # data.cleanup()


if __name__ == '__main__':
    unittest.main()

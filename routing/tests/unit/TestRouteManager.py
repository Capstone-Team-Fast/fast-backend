import datetime
import json
import re
import unittest

from neomodel import config, db

from backend import settings
from routing import constant
from routing.managers import RouteManager
from routing.tests.unit import data


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        route_manager = RouteManager(db_connection=config.DATABASE_URL)
        self.assertIsNone(route_manager.best_assignment)
        self.assertIsNone(route_manager.objective_function_value)
        self.assertListEqual(route_manager.objective_function_values, [])

    def test_request_route_empty_connection_string(self):
        with self.assertRaises(ValueError):
            route_manager = RouteManager(db_connection='')

    def test_request_route_invalid_connection_string(self):
        with self.assertRaises(ValueError):
            route_manager = RouteManager(db_connection='bolt://userpassword@localhost:7687')

    def test_request_route(self):
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes(departure='', locations=[], drivers=[])
        expected_result = json.dumps({
            'solver_status': 5, 'message': 'NO_LOCATIONS_TO_ASSIGN', 'description': 'No location to assign.',
            'others': [], 'routes': []
        })
        self.assertEqual(response, expected_result)

    def test_request_route_base_case(self):
        departure = data.departure
        customers = data.get_random_customers()
        drivers = data.get_random_drivers()

        # Create routes
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes(departure=departure, locations=customers, drivers=drivers)
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
        response = route_manager.request_routes(departure=departure, locations=customers, drivers=drivers)
        log_filename = f'{datetime.datetime.now().strftime(constant.DATETIME_FORMAT)}'
        log_filename = re.sub('[^a-zA-Z\d]', '', log_filename)
        log_filename = log_filename + '.json'
        with open(file=log_filename, mode='w') as file:
            json.dump(json.loads(response), file, ensure_ascii=False, indent=4)

        # Cleanup database
        # data.cleanup()

    def test_request_route_with_invalid_addresses(self):
        departure = data.departure
        customers = data.get_random_customers(n=6)
        drivers = data.get_random_drivers(n=1, min_capacity=10, max_capacity=20)

        # Create routes
        route_manager = RouteManager(db_connection=settings.NEOMODEL_NEO4J_BOLT_URL)
        response = route_manager.request_routes(departure=departure, locations=customers, drivers=drivers)
        log_filename = f'{datetime.datetime.now().strftime(constant.DATETIME_FORMAT)}'
        log_filename = re.sub('[^a-zA-Z\d]', '', log_filename)
        log_filename = log_filename + '.json'
        with open(file=log_filename, mode='w') as file:
            json.dump(json.loads(response), file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    unittest.main()

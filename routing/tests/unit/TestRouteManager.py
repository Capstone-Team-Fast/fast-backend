import json
import unittest

from neomodel import config, db

from backend import settings
from routing.managers import RouteManager


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        route_manager = RouteManager(db_connection=config.DATABASE_URL)
        self.assertIsNone(route_manager.best_assignment)
        self.assertIsNone(route_manager.objective_function_value)
        self.assertListEqual(route_manager.objective_function_values, [])

    def test_request_route(self):
        route_manager = RouteManager(config.DATABASE_URL)
        drivers = [{}]
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
        departure = {}
        response = route_manager.request_routes(departure=departure, locations=locations, drivers=drivers)


if __name__ == '__main__':
    unittest.main()

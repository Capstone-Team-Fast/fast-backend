import json
import unittest

from neomodel import config, db

from backend import settings
from routing import constant
from routing.exceptions import RouteStateException
from routing.models.driver import Driver
from routing.models.location import Pair, Customer
from routing.models.route import Route


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        route = Route().save()
        self.assertIsNone(route.departure)
        self.assertIsNone(route.last_stop)
        self.assertIsNone(route.previous)
        self.assertIsNone(route.driver)
        self.assertTrue(route.is_open)
        self.assertTrue(route.is_empty)
        self.assertEqual(route.total_distance, 0)
        self.assertEqual(route.total_demand, 0)
        self.assertEqual(route.total_duration, 0)
        self.assertEqual(route.itinerary, [])
        route.delete()

    def test_connect_route_driver(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        self.assertEqual(driver, driver.route.driver)
        driver.route.delete()
        driver.delete()

    def test_add_when_no_departure(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        location1 = Customer().save()
        location2 = Customer().save()
        with self.assertRaises(RouteStateException):
            driver.add(Pair(location1, location2))
        driver.delete()
        location1.delete()
        location2.delete()

    def test_route_serializer_template(self):
        route = Route().save()
        expected_result = json.dumps({
            "id": route.id,
            "created_on": route.created_on.strftime(constant.DATETIME_FORMAT),
            "total_quantity": 0,
            "total_distance": 0,
            "total_duration": 0,
            "assigned_to": None,
            "itinerary": []
        })
        self.assertEqual(route.serialize(), expected_result)
        route.delete()


if __name__ == '__main__':
    unittest.main()

import json
import unittest

from neomodel import config, db

from backend import settings
from routing import constant
from routing.models.driver import Driver
from routing.models.route import Route


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_route_serializer_template(self):
        route = Route().save()
        print(route.serialize())
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

    def test_connect_route_driver(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        driver.save_route()
        self.assertEqual(driver.route, driver.route)
        driver.route.delete()
        driver.delete()


if __name__ == '__main__':
    unittest.main()

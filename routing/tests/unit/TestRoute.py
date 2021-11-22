import json
import unittest

from neomodel import config, db

from backend import settings
from routing import constant
from routing.exceptions import RouteStateException
from routing.models.driver import Driver
from routing.models.location import Pair, Customer, Address, Depot
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
        customer1 = Customer().save()
        customer2 = Customer().save()
        with self.assertRaises(RouteStateException):
            driver.add(Pair(customer1, customer2))
        driver.delete()
        customer1.delete()
        customer2.delete()

    def test_add_insert_front_one_location(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(customer_address)
        customer.demand = 4

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.set_address(depot_address)

        route = Route().save()
        route.set_departure(depot)
        self.assertTrue(route.add(customer, Pair(customer, None)))
        self.assertEqual(route.departure, depot)
        self.assertEqual(route.departure.next, customer)
        self.assertEqual(route.departure, customer.previous)
        self.assertTrue(customer.is_assigned)
        self.assertEqual(route.itinerary, [depot, customer])

        customer_address.delete()
        customer.delete()
        depot_address.delete()
        depot.delete()
        route.delete()

    def test_add_when_no_location(self):
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.set_address(depot_address)

        route = Route().save()
        route.set_departure(depot)
        self.assertFalse(route.add(None, None))
        self.assertEqual(route.departure, depot)
        self.assertIsNone(route.departure.next)
        self.assertIsNone(route.departure.previous)
        self.assertEqual(route.itinerary, [])

        depot_address.delete()
        depot.delete()
        route.delete()

    def test_add_when_same_location(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(customer_address)
        customer.demand = 4

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.set_address(depot_address)

        route = Route().save()
        route.set_departure(depot)
        pair = Pair(customer, customer)
        for location in pair.get_pair():
            self.assertTrue(route.add(location, pair))
            self.assertEqual(route.departure, depot)
            self.assertEqual(route.departure.next, customer)
            self.assertEqual(customer.previous, route.departure)
            self.assertEqual(route.itinerary, [depot, customer])

        customer_address.delete()
        customer.delete()
        depot_address.delete()
        depot.delete()
        route.delete()

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

    def test_route_serializer(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(customer_address)
        customer.demand = 4

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.set_address(depot_address)

        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()

        route = Route().save()
        route.set_departure(depot)
        pair = Pair(customer, None)
        for location in pair.get_pair():
            route.add(location, pair)

        route.assigned_to.connect(driver)

        itinerary = []
        for location in [depot, customer]:
            itinerary.append(json.loads(location.serialize()))

        expected_result = json.dumps({
            "id": route.id,
            "created_on": route.created_on.strftime(constant.DATETIME_FORMAT),
            "total_quantity": 4,
            "total_distance": 7.159,
            "total_duration": 13.4,
            "assigned_to": json.loads(driver.serialize()),
            "itinerary": itinerary
        })

        self.assertEqual(route.serialize(), expected_result)

        driver.delete()
        customer_address.delete()
        customer.delete()
        depot_address.delete()
        depot.delete()
        route.delete()


if __name__ == '__main__':
    unittest.main()

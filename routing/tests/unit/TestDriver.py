import unittest
from datetime import datetime, timedelta
from random import randint

from neomodel import config, db

from backend import settings
from routing.exceptions import RouteStateException
from routing.models.driver import Driver
from routing.models.language import Language
from routing.models.location import Address, Depot, Customer, Pair
from routing.models.route import Route


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        driver = Driver(first_name='John', last_name='Doe', employee_status='P')
        self.assertEqual(driver.first_name, 'John')
        self.assertEqual(driver.last_name, 'Doe')
        self.assertEqual(driver.employee_status, 'P')
        self.assertEqual(driver.route, Route())
        self.assertEqual(driver.capacity, 0)
        self.assertIsNone(driver.departure)

    def test_set_departure(self):
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)  # Assign an address to the depot
        driver = Driver(first_name='John', last_name='Doe', employee_status='P')
        driver.set_departure(depot)
        self.assertEqual(driver.departure, depot)
        depot_address.delete()

    def test_add_when_no_departure(self):
        driver = Driver(first_name='John', last_name='Doe', employee_status='P')
        customer1_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer2_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer1_address)
        customer2.geographic_location.connect(customer2_address)
        pair = Pair(customer1, customer2)
        with self.assertRaises(RouteStateException):
            driver.add(pair)
        customer1_address.delete()
        customer2_address.delete()
        customer1.delete()
        customer2.delete()

    def test_add_when_departure_with_not_enough_capacity_enough_time(self):
        depot = Depot.nodes.get(uid='02105dce66264b0ab3f6dbad0e4934b9')
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10)
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(1, 5))
        customer1 = Customer.nodes.get(uid='697d18493c6f4ed1b7be35b089f81d66')
        customer1.demand = 11
        customer2 = Customer.nodes.get(uid='9193a2011d344672922a089801c8bd82')
        customer2.demand = 15
        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertFalse(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

    def test_add_when_departure_with_enough_capacity_for_one_location_enough_time_for_all_locations(self):
        depot = Depot.nodes.get(uid='02105dce66264b0ab3f6dbad0e4934b9')
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10)
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(1, 5))
        customer1 = Customer.nodes.get(uid='697d18493c6f4ed1b7be35b089f81d66')
        customer1.demand = 8
        customer2 = Customer.nodes.get(uid='9193a2011d344672922a089801c8bd82')
        customer2.demand = 11
        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

    def test_add_when_departure_with_enough_capacity_and_time_for_all_locations(self):
        depot = Depot.nodes.get(uid='02105dce66264b0ab3f6dbad0e4934b9')
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=20)
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(1, 5))
        customer1 = Customer.nodes.get(uid='697d18493c6f4ed1b7be35b089f81d66')
        customer1.demand = 8
        customer2 = Customer.nodes.get(uid='9193a2011d344672922a089801c8bd82')
        customer2.demand = 11
        pair = Pair(customer1, customer2)
        self.assertTrue(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertTrue(customer2.is_assigned)

    def test_add_when_departure_with_enough_capacity_and_not_enough_time_for_all_locations(self):
        depot = Depot.nodes.get(uid='02105dce66264b0ab3f6dbad0e4934b9')
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=20)
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(minutes=randint(1, 5))
        customer1 = Customer.nodes.get(uid='697d18493c6f4ed1b7be35b089f81d66')
        customer1.demand = 8
        customer2 = Customer.nodes.get(uid='9193a2011d344672922a089801c8bd82')
        customer2.demand = 11
        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertFalse(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

    def test_add_when_departure_with_enough_capacity_and_time_same_locations(self):
        depot = Depot.nodes.get(uid='02105dce66264b0ab3f6dbad0e4934b9')
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=20)
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(minutes=randint(14, 20))
        customer1 = Customer.nodes.get(uid='697d18493c6f4ed1b7be35b089f81d66')
        customer1.demand = 8
        customer2 = Customer.nodes.get(uid='9193a2011d344672922a089801c8bd82')
        customer2.demand = 11
        pair = Pair(customer1, customer2)
        self.assertTrue(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertTrue(customer2.is_assigned)

    def test_driver_availability(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        languages = [Language(language=language).save() for language in ['English', 'Spanish', 'Mandarin']]
        [driver.language.connect(language) for language in languages]
        print(driver.language.all())
        print(driver.get_availability())
        self.assertEqual(driver.get_availability().sort(), languages.sort())
        driver.delete()
        [language.delete() for language in languages]


if __name__ == '__main__':
    unittest.main()

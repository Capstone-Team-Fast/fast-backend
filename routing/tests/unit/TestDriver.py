import unittest

from neomodel import config, db

from backend import settings
from routing.exceptions import RouteStateException
from routing.models.driver import Driver
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
        depot.geographic_location.connect(depot_address)    # Assign an address to the depot
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

    def test_add_when_departure_with_not_enough_capacity(self):
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)  # Assign an address to the depot
        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10)
        driver.set_departure(depot)
        customer1_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer2_address = Address(address='1400 R St', city='Lincoln', state='NE', zipcode=68588).save()
        customer1 = Customer(demand=11).save()
        customer2 = Customer(demand=15).save()
        customer1.geographic_location.connect(customer1_address)
        customer2.geographic_location.connect(customer2_address)
        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        customer1_address.delete()
        customer2_address.delete()
        customer1.delete()
        customer2.delete()






if __name__ == '__main__':
    unittest.main()

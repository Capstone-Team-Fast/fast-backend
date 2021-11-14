import json
import unittest
from datetime import datetime, timedelta
from random import randint

from neomodel import config, db

from backend import settings
from routing.exceptions import RouteStateException
from routing.models.availability import Availability
from routing.models.driver import Driver
from routing.models.language import Language
from routing.models.location import Address, Depot, Customer, Pair
from routing.models.route import Route


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        driver = Driver(first_name='John', last_name='Doe', employee_status='P').save()
        self.assertEqual(driver.first_name, 'John')
        self.assertEqual(driver.last_name, 'Doe')
        self.assertEqual(driver.employee_status, 'P')
        self.assertEqual(driver.route, Route())
        self.assertEqual(driver.capacity, 0)
        self.assertIsNone(driver.departure)
        driver.delete()

    def test_set_departure(self):
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)  # Assign an address to the depot
        driver = Driver(first_name='John', last_name='Doe', employee_status='P').save()
        driver.set_departure(depot)
        self.assertEqual(driver.departure, depot)
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_add_when_no_departure(self):
        driver = Driver(first_name='John', last_name='Doe', employee_status='P').save()
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        pair = Pair(customer1, customer2)
        with self.assertRaises(RouteStateException):
            driver.add(pair)
        customer_address.delete()
        customer1.delete()
        customer2.delete()
        driver.delete()

    def test_add_when_departure_with_not_enough_capacity_enough_time(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        customer1.demand = 11
        customer2.demand = 15

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)  # Assign an address to the depot

        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10).save()
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(1, 5))
        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertFalse(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

        customer_address.delete()
        customer1.delete()
        customer2.delete()
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_add_when_departure_with_enough_capacity_for_one_location_enough_time_for_all_locations(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        customer1.demand = 8
        customer2.demand = 11

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)

        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10).save()
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(15, 20))

        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

        customer_address.delete()
        customer1.delete()
        customer2.delete()
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_add_when_departure_with_enough_capacity_and_time_for_all_locations(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        customer1.demand = 8
        customer2.demand = 11

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)

        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=20).save()
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(hours=randint(15, 20))

        pair = Pair(customer1, customer2)
        self.assertTrue(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertTrue(customer2.is_assigned)

        customer_address.delete()
        customer1.delete()
        customer2.delete()
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_add_when_departure_with_enough_capacity_and_enough_time_one_location(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        customer1.demand = 8
        customer2.demand = 11

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)

        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=10).save()
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(minutes=randint(20, 30))

        pair = Pair(customer1, customer2)
        self.assertFalse(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertFalse(customer2.is_assigned)

        customer_address.delete()
        customer1.delete()
        customer2.delete()
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_add_when_departure_with_enough_capacity_and_time_same_locations(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer1 = Customer().save()
        customer2 = Customer().save()
        customer1.geographic_location.connect(customer_address)
        customer2.geographic_location.connect(customer_address)
        customer1.demand = 8
        customer2.demand = 11

        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        depot = Depot().save()
        depot.geographic_location.connect(depot_address)

        driver = Driver(first_name='John', last_name='Doe', employee_status='P', capacity=20).save()
        driver.set_departure(depot)
        driver.start_time = datetime.now()
        driver.end_time = driver.start_time + timedelta(minutes=randint(15, 20))

        pair = Pair(customer1, customer2)
        self.assertTrue(driver.add(pair))
        self.assertTrue(customer1.is_assigned)
        self.assertTrue(customer2.is_assigned)

        customer_address.delete()
        customer1.delete()
        customer2.delete()
        depot_address.delete()
        depot.delete()
        driver.delete()

    def test_driver_availability(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        languages = [Language(language=language).save() for language in ['English', 'Spanish', 'Mandarin']]
        [driver.language.connect(language) for language in languages]
        self.assertEqual(driver.get_languages().sort(), languages.sort())
        driver.delete()
        [language.delete() for language in languages]

    def test_driver_with_no_language(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        self.assertEqual(driver.get_languages(), [])
        driver.delete()

    def test_driver_str(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        self.assertEqual(str(driver), 'Last,First')
        driver.delete()

    def test_driver_is_volunteer(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        self.assertFalse(driver.is_volunteer())
        driver.delete()

    def test_driver_is_full_time(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        self.assertTrue(driver.is_full_time())
        driver.delete()

    def test_serializer_template(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        expected_result = json.dumps({
            "id": None,
            "capacity": 20,
            "employee_status": "P",
            "availability": [],
            "languages": []
        })
        self.assertEqual(driver.serialize(), expected_result)
        driver.delete()

    def test_serializer_languages(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        languages = [Language(language=language).save() for language in Language.options()]
        [driver.language.connect(language) for language in languages]
        languages.sort()
        expected_result = json.dumps({
            "id": None,
            "capacity": 20,
            "employee_status": "P",
            "availability": [],
            "languages": [language.serialize() for language in languages]
        })
        self.assertEqual(driver.serialize(), expected_result)
        [language.delete() for language in languages]
        driver.delete()

    def test_serializer_availability(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        availabilities = [Availability(day=day).save() for day in Availability.options()]
        [driver.is_available_on.connect(availability) for availability in availabilities]
        availabilities.sort()
        expected_result = json.dumps({
            "id": None,
            "capacity": 20,
            "employee_status": "P",
            "availability": [availability.serialize() for availability in availabilities],
            "languages": []
        })
        self.assertEqual(driver.serialize(), expected_result)
        [availability.delete() for availability in availabilities]
        driver.delete()

    def test_serializer_language_and_availability(self):
        driver = Driver(first_name='First', last_name='Last', employee_status='P', capacity=20).save()
        availabilities = [Availability(day=day).save() for day in Availability.options()]
        [driver.is_available_on.connect(availability) for availability in availabilities]

        languages = [Language(language=language).save() for language in Language.options()]
        [driver.language.connect(language) for language in languages]

        print(driver.serialize())
        availabilities.sort()
        expected_result = json.dumps({
            "id": None,
            "capacity": 20,
            "employee_status": "P",
            "availability": [availability.serialize() for availability in availabilities],
            "languages": [language.serialize() for language in languages]
        })
        print(expected_result)
        self.assertEqual(driver.serialize(), expected_result)
        [availability.delete() for availability in availabilities]
        driver.delete()


if __name__ == '__main__':
    unittest.main()

import json
import unittest

from neomodel import config, db

from backend import settings
from routing.exceptions import LocationStateException
from routing.models.language import Language
from routing.models.location import Customer, Depot, Address


class MyTestCase(unittest.TestCase):
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    def test_constructor(self):
        customer = Customer().save()
        self.assertFalse(customer.is_center)
        self.assertFalse(customer.is_assigned)
        self.assertIsNone(customer.previous)
        self.assertIsNone(customer.next)
        self.assertIsNone(customer.address)
        customer.delete()

    def test_reset(self):
        customer = Customer()
        customer.previous = Customer()
        customer.next = Customer()
        customer.reset()
        self.assertIsNone(customer.next)
        self.assertIsNone(customer.previous)

    def test_equal(self):
        customer1 = Customer().save()
        customer2 = Customer().save()
        self.assertTrue(customer1 == customer2)
        customer1.delete()
        customer2.delete()

    def test_duration_none_objects(self):
        customer1 = Customer().save()
        customer2 = Customer().save()
        with self.assertRaises(LocationStateException):
            customer1.duration(customer2)
        customer1.delete()
        customer2.delete()

    def test_distance_none_objects(self):
        customer1 = Customer().save()
        customer2 = Customer().save()
        with self.assertRaises(LocationStateException):
            customer1.distance(customer2)
        customer1.delete()
        customer2.delete()

    def test_is_center(self):
        customer = Customer().save()
        depot = Depot().save()
        self.assertFalse(customer.is_center)
        self.assertTrue(depot.is_center)
        customer.delete()
        depot.delete()

    def test_distance_and_duration_between_depot_customer_none(self):
        customer = Customer().save()
        depot = Depot().save()
        with self.assertRaises(LocationStateException):
            customer.duration(depot)
        with self.assertRaises(LocationStateException):
            customer.distance(depot)
        customer.delete()
        depot.delete()

    def test_distance_and_duration_between_depot_customer(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        expected_distance = 7.27
        expected_duration = 14.1
        customer = Customer().save()
        depot = Depot().save()
        customer.geographic_location.connect(customer_address)
        depot.geographic_location.connect(depot_address)
        self.assertEqual(customer.duration(depot), expected_duration)
        self.assertEqual(customer.distance(depot), expected_distance)
        customer.delete()
        depot.delete()

    def test_serializer_template(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.geographic_location.connect(address)
        expected_result = json.dumps({
            'id': customer.external_id,
            'is_center': False,
            'address': customer.address.serialize(),
            'demand': customer.demand,
            'languages': []
        })
        print(type(customer.serialize()))
        print(customer.serialize())
        print(json.loads(expected_result))
        print(expected_result)
        self.assertEqual(customer.serialize(), expected_result)
        address.delete()
        customer.delete()

    def test_serializer_languages(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.geographic_location.connect(address)

        languages = [Language(language=language).save() for language in Language.options()]
        [customer.language.connect(language) for language in languages]
        languages.sort()

        expected_result = json.dumps({
            'id': customer.external_id,
            'is_center': False,
            'address': customer.address.serialize(),
            'demand': customer.demand,
            'languages': [language.serialize() for language in languages]
        })
        self.assertEqual(customer.serialize(), expected_result)
        address.delete()
        [language.delete() for language in languages]
        customer.delete()


if __name__ == '__main__':
    unittest.main()

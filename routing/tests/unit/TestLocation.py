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

    def test_constructor_with_no_address(self):
        customer = Customer().save()
        self.assertFalse(customer.is_center)
        self.assertFalse(customer.is_assigned)
        self.assertIsNone(customer.previous)
        self.assertIsNone(customer.next)
        self.assertIsNone(customer.address)
        customer.delete()

    def test_constructor(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182)
        customer = Customer().save()
        customer.set_address(address)
        self.assertFalse(customer.is_center)
        self.assertFalse(customer.is_assigned)
        self.assertIsNone(customer.previous)
        self.assertIsNone(customer.next)
        self.assertEqual(customer.address, address)
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

    def test_set_address_one_address(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(customer_address)
        self.assertEqual(customer.address, customer_address)
        customer_address.delete()
        customer.delete()

    def test_set_address_update(self):
        old_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        new_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        customer = Customer().save()
        customer.set_address(old_address)
        self.assertEqual(customer.address, old_address)
        customer.set_address(new_address)
        self.assertEqual(customer.address, new_address)
        old_address.delete()
        new_address.delete()
        customer.delete()

    def test_distance_and_duration_between_depot_customer(self):
        customer_address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        depot_address = Address(address='602 N. 20th St', city='Omaha', state='NE', zipcode=68178).save()
        expected_distance = 7.27
        expected_duration = 14.1
        customer = Customer().save()
        depot = Depot().save()
        customer.set_address(customer_address)
        depot.set_address(depot_address)
        self.assertEqual(customer.duration(depot), expected_duration)
        self.assertEqual(customer.distance(depot), expected_distance)
        customer.delete()
        depot.delete()

    def test_serializer_template(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(address)
        expected_result = json.dumps({
            'id': customer.external_id,
            'is_center': False,
            'address': customer.address.serialize(),
            'demand': customer.demand,
            'languages': []
        })
        self.assertEqual(customer.serialize(), expected_result)
        address.delete()
        customer.delete()

    def test_serializer_customer_with_languages(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        customer = Customer().save()
        customer.set_address(address)

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

    def test_serializer_depot(self):
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182).save()
        depot = Depot().save()
        depot.set_address(address)

        expected_result = json.dumps({
            'id': depot.external_id,
            'is_center': True,
            'address': depot.address.serialize()
        })

        self.assertEqual(depot.serialize(), expected_result)
        address.delete()
        depot.delete()


if __name__ == '__main__':
    unittest.main()

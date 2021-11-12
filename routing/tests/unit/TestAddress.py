import unittest

from routing.models.location import Address


class MyTestCase(unittest.TestCase):
    def test_constructor(self):
        street = '9029 Burt St'
        city = 'Omaha'
        state = 'NE'
        zipcode = 68114
        address = Address(address=street, city=city, state=state, zipcode=zipcode)
        self.assertEqual(address.address, street)
        self.assertEqual(address.city, city)
        self.assertEqual(address.state, state)
        self.assertEqual(address.zipcode, zipcode)
        self.assertIsNone(address.latitude)
        self.assertIsNone(address.longitude)
        with self.assertRaises(ValueError):
            address.neighbor.get()

    def test_str(self):
        street = '9029 Burt St'
        city = 'Omaha'
        state = 'NE'
        zipcode = 68114
        address = Address(address=street, city=city, state=state, zipcode=zipcode)
        expected = '{address}, {city}, {state} {zipcode}'.format(address=street, city=city, state=state,
                                                                 zipcode=zipcode)
        self.assertEqual(str(address), expected)

    def test_distance_value_error(self):
        address = Address(address=None, city=None, state=None, zipcode=None)
        with self.assertRaises(ValueError):
            address.distance(object)

    def test_duration_value_error(self):
        address = Address(address=None, city=None, state=None, zipcode=None)
        with self.assertRaises(ValueError):
            address.duration(object)


if __name__ == '__main__':
    unittest.main()

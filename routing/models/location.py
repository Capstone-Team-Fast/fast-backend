import json
import os
import sys
from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, \
    DateTimeProperty, UniqueIdProperty, Relationship, StructuredRel, One, DoesNotExist, AttemptedCardinalityViolation

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing.exceptions import LocationStateException


class _Weight(StructuredRel):
    """This class defines the edge between two Addresses.

    An edge have distance and duration, and may have a savings.
    """
    distance = FloatProperty(required=True)
    duration = FloatProperty(required=True)
    savings = FloatProperty()


class Address(StructuredNode):
    """This class defines an Address node.

    An address is a standard US address and has the following properties:
        address, city, state, zipcode, country.

        Typical usage example:
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182)
        address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182, country='US')
    """

    """A unique id assigned upon creating this object"""
    uid = UniqueIdProperty()

    """A string representing the street of this address. It is a required property."""
    address = StringProperty(index=True, required=True)

    """A string representing the city of this address. It is a required property."""
    city = StringProperty(index=True, required=True)

    """A string representing the state of this address. It is a required property."""
    state = StringProperty(index=True, required=True)

    """A string representing the zipcode of this address. It is a required property."""
    zipcode = IntegerProperty(index=True, required=True)

    """A string representing the country of this address. If no value is provided it defaults to 'United States'."""
    country = StringProperty(index=True, default='United States')

    """A float representing the latitude of this address. It is an optional property."""
    latitude = FloatProperty(index=True)

    """A float representing the longitude of this address. It is an optional property."""
    longitude = FloatProperty(index=True)

    """An integer representing the maximum number of addresses this driver can deliver to."""
    created_on = DateTimeProperty(index=True, default=datetime.now)

    """A datetime object representing the last modified datetime of this driver."""
    modified_on = DateTimeProperty(index=True, default_now=True)

    """An integer representing the id of this driver."""
    external_id = IntegerProperty(required=False, unique_index=True)

    """A relationship addresses that can be reached from this address."""
    neighbor = Relationship(cls_name='Address', rel_type='CONNECTED_TO', model=_Weight)

    def __init__(self, *args, **kwargs):
        """Creates an Address.

            Typical usage example:

            address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182)
            address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182, country='US')
        """
        super(Address, self).__init__(*args, **kwargs)

    def distance(self, other):
        """Provides the mechanism for getting the distance between this address and another address.

        This method returns a positive float value if one address is directly connected to another. Otherwise, None is
        returned.

        @param
        @return
        @raise
        """
        if isinstance(other, type(self)):
            if self == other:
                return 0.0
            self.__validate_edge_with(other)
            return self.neighbor.relationship(other).distance if self.neighbor.relationship(other) else None
        raise TypeError(f'{type(other)} is not supported.')

    def duration(self, other):
        if isinstance(other, type(self)):
            if self == other:
                return 0.0
            self.__validate_edge_with(other)
            return self.neighbor.relationship(other).duration if self.neighbor.relationship(other) else None
        raise TypeError(f'{type(other)} is not supported.')

    def __validate_edge_with(self, other):
        from routing.services import BingMatrixService
        if isinstance(other, type(self)):
            if self == other:
                return True
            else:
                if self.neighbor.relationship(other):
                    return True
                else:
                    BingMatrixService.build_matrices(start=self, end=[other])
                return True
        raise TypeError(f'{type(other)} is not supported.')

    @classmethod
    def category(cls):
        pass

    def serialize(self):
        obj = json.dumps({
            'id': self.external_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude
            }
        })
        return obj

    def __hash__(self):
        return hash((self.address, self.city, self.state, self.zipcode))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.address == other.address and self.city == other.city
                    and self.state == other.state and self.zipcode == other.zipcode)
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{address}, {city}, {state} {zipcode}'.format(address=self.address, city=self.city, state=self.state,
                                                             zipcode=self.zipcode)


class Location(StructuredNode):
    __abstract_node__ = True
    is_center = BooleanProperty(index=True, default=False)
    uid = UniqueIdProperty()
    external_id = IntegerProperty(required=False, unique_index=True)
    created_on = DateTimeProperty(index=True, default=datetime.now)
    modified_on = DateTimeProperty(index=True, default_now=True)
    __geographic_location = Relationship(cls_name='Address', rel_type='LOCATED_AT', cardinality=One)

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.is_assigned = False
        self.next = None
        self.previous = None

    def set_address(self, address):
        if address is None:
            raise TypeError(f'Type {type(address)} not supported. Supply type {type(Address)}.')

        if address in Address.nodes.all():
            node_set = Address.nodes.filter(address=address.address, city=address.city, state=address.state,
                                            zipcode=address.zipcode)
            address = node_set[0]
        else:
            address = Address(address=address.address, city=address.city, state=address.state,
                              zipcode=address.zipcode).save()
        try:
            self.__geographic_location.connect(address)
        except AttemptedCardinalityViolation:
            self.__geographic_location.reconnect(self.address, address)

    @property
    def address(self):
        try:
            return self.__geographic_location.get()
        except DoesNotExist:
            return None

    def reset(self):
        self.next = None
        self.previous = None

    def __eq__(self, other):
        if issubclass(type(other), Location) and issubclass(type(self), Location):
            equal = False
            try:
                if self.external_id and other.external_id:
                    equal = self.external_id == other.external_id and self.is_center == other.is_center
            except AttributeError:
                pass
            return equal
        raise TypeError(f'{type(other)} and {type(self)} do not subclass {Location}.')

    def __hash__(self):
        return hash(self.address)

    def duration(self, other):
        """Gets the duration (in minutes) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if issubclass(type(other), Location) and issubclass(type(self), Location):
            if self.address is None and other.address is None:
                raise LocationStateException(f'{self} and {other} have no addresses.')
            elif self.address is None:
                raise LocationStateException(f'{self} has no address.')
            elif other.address is None:
                raise LocationStateException(f'{other} has no address.')
            if self == other:
                return 0.0
            return self.address.duration(other.address)
        raise TypeError(f'{type(other)} does not subclass {type(self)}.')

    def distance(self, other):
        """Gets the distance (in meters) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if issubclass(type(other), Location) and issubclass(type(self), Location):
            if self.address is None and other.address is None:
                raise LocationStateException(f'{self} and {other} have no addresses.')
            elif self.address is None:
                raise LocationStateException(f'{self} has no address.')
            elif other.address is None:
                raise LocationStateException(f'{other} has no address.')
            if self == other:
                return 0.0
            return self.address.distance(other.address)
        raise TypeError(f'{type(other)} does not subclass {type(self)}.')

    def __str__(self):
        return 'UID: {} at address {}'.format(self.uid, self.address)

    def serialize(self):
        obj = json.dumps({
            'id': self.external_id,
            'is_center': self.is_center,
            'address': json.loads(self.address.serialize())
        })
        return obj

    @classmethod
    def category(cls):
        pass


class Customer(Location):
    demand = IntegerProperty(index=True)
    language = Relationship(cls_name='routing.models.language.Language', rel_type='SPEAKS')

    def __init__(self, *args, **kwargs):
        super(Customer, self).__init__(*args, **kwargs)

    def get_languages(self):
        return self.language.all()

    def serialize(self):
        obj = json.loads(super(Customer, self).serialize())
        languages = self.get_languages()
        if languages:
            languages.sort()
            languages = [json.loads(language.serialize()) for language in languages]
        else:
            languages = []

        obj.update({
            'demand': self.demand,
            'languages': languages
        })
        return json.dumps(obj)


class Depot(Location):
    is_center = BooleanProperty(index=True, default=True)

    def __init__(self, *args, **kwargs):
        super(Depot, self).__init__(*args, **kwargs)

    def serialize(self):
        return super(Depot, self).serialize()


class Pair:
    def __init__(self, location1: Location, location2: Location):
        self.__location1 = location1
        self.__location2 = location2
        self.__origin = None
        self.__distance_saving = None

    def set_origin(self, origin):
        self.__origin = origin

    def set_saving(self, saving):
        self.__distance_saving = saving

    @property
    def distance_saving(self):
        return self.__distance_saving

    @property
    def origin(self):
        return self.__origin

    def is_first(self, location: Location):
        return self.__location1 == location

    def is_last(self, location: Location):
        return self.__location2 == location

    @property
    def first(self):
        return self.__location1

    @property
    def last(self):
        return self.__location2

    def get_pair(self):
        return self.__location1, self.__location2

    def is_assignable(self):
        if self.__location1 and self.__location2:
            return not (self.__location1.is_assigned or self.__location2.is_assigned)
        elif (self.__location1 is None and self.__location2) or (self.__location1 and self.__location2 is None):
            return True

        return False

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.__distance_saving == other.__distance_saving
        raise ValueError(f'Type {type(other)} not supported.')

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.__distance_saving < other.__distance_saving
        raise ValueError(f'Type {type(other)} not supported.')

    def __str__(self):
        return '({}, {})'.format(self.__location1, self.__location2)

import json
import os
import sys
from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, \
    DateTimeProperty, UniqueIdProperty, Relationship, StructuredRel, One, DoesNotExist

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing.exceptions import LocationStateException


class Weight(StructuredRel):
    distance = FloatProperty(required=True)
    duration = FloatProperty(required=True)
    savings = FloatProperty()


class Address(StructuredNode):
    uid = UniqueIdProperty()
    address = StringProperty(index=True, required=True)
    city = StringProperty(index=True, required=True)
    state = StringProperty(index=True, required=True)
    zipcode = IntegerProperty(index=True, required=True)
    latitude = FloatProperty(index=True)
    longitude = FloatProperty(index=True)
    created_on = DateTimeProperty(index=True, default=datetime.now)
    modified_on = DateTimeProperty(index=True, default_now=True)
    external_id = IntegerProperty(required=False, unique_index=True)

    neighbor = Relationship(cls_name='Address', rel_type='CONNECTED_TO', model=Weight)

    def __init__(self, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)

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

    def distance(self, other):
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


class Location(StructuredNode):
    __abstract_node__ = True
    is_center = BooleanProperty(index=True, default=False)
    uid = UniqueIdProperty()
    external_id = IntegerProperty(required=False, unique_index=True)
    created_on = DateTimeProperty(index=True, default=datetime.now)
    modified_on = DateTimeProperty(index=True, default_now=True)
    geographic_location = Relationship(cls_name='Address', rel_type='LOCATED_AT', cardinality=One)

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.is_assigned = False
        self.next = None
        self.previous = None

    @property
    def address(self) -> Address:
        try:
            return self.geographic_location.get()
        except DoesNotExist:
            pass

    def reset(self):
        self.next = None
        self.previous = None

    def __eq__(self, other):
        if issubclass(type(other), Location) and issubclass(type(self), Location):
            return self.address == other.address
        raise TypeError(f'{type(other)} and {type(self)} do not subclass {Location}.')

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
            'address': self.address.serialize()
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
            languages = [language.serialize() for language in languages]
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


class Pair:
    def __init__(self, location1: Location, location2: Location):
        self.location1 = location1
        self.location2 = location2

    def is_first(self, location: Location):
        return self.location1 == location

    def is_last(self, location: Location):
        return self.location2 == location

    @property
    def first(self):
        return self.location1

    @property
    def last(self):
        return self.location2

    def get_pair(self):
        return self.location1, self.location2

    def is_assignable(self):
        if self.location1 and self.location2:
            return not (self.location1.is_assigned or self.location2.is_assigned)
        elif (self.location1 is None and self.location2) or (self.location1 and self.location2 is None):
            return True

        return False

    def __str__(self):
        return '({}, {})'.format(self.location1, self.location2)

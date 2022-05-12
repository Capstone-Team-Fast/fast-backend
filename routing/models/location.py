import json
import os
import sys
from datetime import datetime

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, \
    DateTimeProperty, UniqueIdProperty, Relationship, RelationshipTo, StructuredRel, One, DoesNotExist, AttemptedCardinalityViolation

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

class Pair_Rel(StructuredRel):
    pass

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

    """A datetime object representing the creation datetime of this driver."""
    created_on = DateTimeProperty(index=True, default=datetime.now)

    """A datetime object representing the last modified datetime of this driver."""
    modified_on = DateTimeProperty(index=True, default_now=True)

    """An integer representing the id of this driver."""
    external_id = IntegerProperty(required=False, unique_index=True)

    """A relationship to addresses that can be reached from this address."""
    neighbor = Relationship(cls_name='Address', rel_type='CONNECTED_TO', model=_Weight)

    def __init__(self, *args, **kwargs):
        """Creates an Address.

            Typical usage example:

            address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182)
            address = Address(address='6001 Dodge St', city='Omaha', state='NE', zipcode=68182, country='US')
        """
        super(Address, self).__init__(*args, **kwargs)

    def distance(self, other):
        """Provides the mechanism for getting the distance between this address and another one.

        This method returns a positive float value if these addresses are directly connected. Otherwise, None is
        returned.

        @param other: Another object to get the distance in-between.
        @return a float representing the distance between these addresses.
        @raise TypeError if other is not a ADDRESS.
        """
        if isinstance(other, type(self)):
            if self == other:
                return 0.0
            self.__validate_edge_with(other)
            return self.neighbor.relationship(other).distance if self.neighbor.relationship(other) else None
        raise TypeError(f'{type(other)} is not supported.')

    def duration(self, other):
        """Provides the mechanism for getting the duration between this address and another one.

        This method returns a positive float value if these addresses are directly connected. Otherwise, None is
        returned.

        @param other: Another object to get the duration in-between.
        @return a float representing the duration between these addresses.
        @raise TypeError if OTHER is not a ADDRESS.
        """
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
        """Serializes this address.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this route.

                Format:
                {
                    'id': [INTEGER],
                    'address': [STRING],
                    'city': [STRING],
                    'state': [STRING],
                    'zipcode': [INTEGER],
                    'coordinates': {
                        'latitude': [FLOAT],
                        'longitude': [FLOAT]
                    }
                }

        @return: A JSON object representing this ADDRESS.
        """
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
    """This abstract class defines a Location node.

    A Location is represented as a linked list node and encapsulation an Address node.
    """
    __abstract_node__ = True

    """A boolean to determine if this location is a depot. By default, a location is not a departure location."""
    is_center = BooleanProperty(index=True, default=False)

    """A unique id assigned upon creating this object"""
    uid = UniqueIdProperty()

    """An integer representing the id of this location."""
    external_id = IntegerProperty(required=False, unique_index=True)

    """A datetime object representing the creation datetime of this location."""
    created_on = DateTimeProperty(index=True, default=datetime.now)

    """A datetime object representing the last modified datetime of this location."""
    modified_on = DateTimeProperty(index=True, default_now=True)

    """A relationship representing the physical address of this location."""
    __geographic_location = Relationship(cls_name='Address', rel_type='LOCATED_AT', cardinality=One)


    is_location_1_of = RelationshipTo(cls_name='Pair', rel_type='LOCATION_1_OF', cardinality=One)
    is_location_2_of = RelationshipTo(cls_name='Pair', rel_type='LOCATION_2_OF', cardinality=One)
    is_origin_of = RelationshipTo(cls_name='Pair', rel_type='ORIGIN_OF', cardinality=One)


    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.is_assigned = False
        self.next = None
        self.previous = None

    def set_address(self, address):
        """Provides the mechanism for setting the physical address of this location.

        This method can also be used to update the address of an existing location. This ensures that a location has one
        and only one address.
        """
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
        """A property to get the address of this location.

        @return the physical address of this location. If no address is assigned, return None.
        """
        try:
            return self.__geographic_location.get()
        except DoesNotExist:
            return None

    def reset(self):
        """Provides the mechanism to clear the next and previous references of this node."""
        self.next = None
        self.previous = None

    def duration(self, other):
        """Provides the mechanism to get the duration (in minutes) between these two locations.

        This implementation guarantees that either location is in the graph database.

        @param other: An object preferably of Location type.
        @return A float representing the duration between this location and another location.
        @raise TypeError if OTHER does not subclass LOCATION.
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
        """Provides the mechanism to get the distance (in miles) between these two locations.

        This implementation guarantees that either location is in the graph database.

        @param other: An object preferably of Location type.
        @return A float representing the distance between this location and another location.
        @raise TypeError if OTHER does not subclass LOCATION.
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

    def serialize(self):
        """Serializes this location.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this location.

                Format:
                {
                    'id': [INTEGER],
                    'is_center': [BOOLEAN],
                    'address': [ADDRESS]
                }

        @return: A JSON object representing this LOCATION.
        """
        obj = json.dumps({
            'id': self.external_id,
            'is_center': self.is_center,
            'address': json.loads(self.address.serialize())
        })
        return obj

    def __str__(self):
        return 'UID: {} at address {}'.format(self.uid, self.address)

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

    @classmethod
    def category(cls):
        pass


class Customer(Location):
    """This class defines a Customer node.

    A Customer is a special Location which has a demand and a set of Languages.

        Typical usage example:

        customer = Customer()
    """
    demand = IntegerProperty(index=True)
    language = Relationship(cls_name='routing.models.language.Language', rel_type='SPEAKS')

    def __init__(self, *args, **kwargs):
        """Creates a Customer."""
        super(Customer, self).__init__(*args, **kwargs)

    def get_languages(self):
        """Provides the mechanism to get the languages spoken by this customer.

        The returned values, if any, is an object of LANGUAGE node.

        @return the list of languages spoken by this customer, otherwise return None.
        """
        return self.language.all()

    def serialize(self):
        """Serializes this customer.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this customer.

                Format:
                {
                    'id': [INTEGER],
                    'is_center': [BOOLEAN],
                    'address': [ADDRESS],
                    'demand': [FLOAT],
                    'languages': [LANGUAGE]
                }

        @return: A JSON object representing this CUSTOMER.
        """
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
    
    
    """A boolean to determine if this depot is considered as a departure location. By default, any depot is a departure location."""
    is_center = BooleanProperty(index=True, default=True)

    def __init__(self, *args, **kwargs):
        """Creates a Depot node."""
        super(Depot, self).__init__(*args, **kwargs)

    def serialize(self):
        """Serializes this depot.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this depot.

                Format:
                {
                    'id': [INTEGER],
                    'is_center': [BOOLEAN],
                    'address': [ADDRESS]
                }

        @return: A JSON object representing this DEPOT.
        """
        return super(Depot, self).serialize()


class Pair(StructuredNode): # made into Structured Node
    """Creates a Pair of locations.

    This class is a utility class to compute the savings between two locations.

        Typical usage example:
        pair = Pair(location1, location2)
    """
    def __init__(self, location1: Location, location2: Location):
        """Creates a Pair of locations based on the arguments.

        @param location1: First location of this pair.
        @param location2: Second location of this pair.
        """
        self.__location1 = location1
        self.__location2 = location2
        self.__origin = None
        self.__distance_saving = None

    def set_origin(self, origin):
        """Provides the mechanism to set the origin of this pair.

        Viewed in a 2D plane, the origin represents the origin of the plan. The position of any location is relative to
        the origin. Thus, two pairs with different origins may not have the same properties. Also, changing the origin
        of a pair does not enforce (re)computation of the distance saved from the origin to the locations.
        """
        self.__origin = origin

    def set_saving(self, saving):
        """Provides the mechanism to set the distance saved by going from the pair's origin to the locations that
        constitute the pair.
        """
        self.__distance_saving = saving

    @property
    def distance_saving(self):
        """A property to retrieve the savings distance from the origin to the locations."""
        return self.__distance_saving

    @property
    def origin(self):
        """A property to retrieve the origin of this pair.

        Viewed in a 2D plane, the origin represents the origin of the plane. The position of any location is relative to
        the origin.
        """
        return self.__origin

    def is_first(self, location: Location):
        """Determines if the location argument is the first location of this pair.

        @return True if the location argument is the first location of this pair, otherwise, False.
        """
        return self.__location1 == location

    def is_last(self, location: Location):
        """Determines if the location argument is the last/second location of this pair.

        @return True if the location argument is the last/second location of this pair, otherwise, False.
        """
        return self.__location2 == location

    @property
    def first(self):
        """A property to retrieve the first location of this pair."""
        return self.__location1

    @property
    def last(self):
        """A property to retrieve the last/second location of this pair."""
        return self.__location2

    def get_pair(self):
        """Retrieves a tuple representing this pair.

        @return a tuple representing the locations of this pair.
        """
        return self.__location1, self.__location2

    def is_assignable(self):
        """Provides the mechanism to determine if a pair is assignable.

        A pair is assignable if at least one of its locations is not assigned.
        """
        if self.__location1 and self.__location2:
            return not (self.__location1.is_assigned or self.__location2.is_assigned)
        elif (self.__location1 is None and self.__location2) or (self.__location1 and self.__location2 is None):
            return True

        return False

    def serialize(self):
        pass

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

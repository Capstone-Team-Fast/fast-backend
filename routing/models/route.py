import copy
import json
import logging
import os
import sys
from collections import deque
from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty, UniqueIdProperty, One, \
    DoesNotExist

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing import constant
from routing.models.location import Pair, Location
from routing.exceptions import EmptyRouteException, RouteStateException


class Route(StructuredNode):
    """This class defines a Route node.

    A Route is constructed as a linked list. Each node represents a Location.
    """

    """A unique id assigned upon creating this object"""
    uid = UniqueIdProperty()

    __quantity = FloatProperty(index=True, default=None)
    __distance = FloatProperty(index=True, default=None)
    __duration = FloatProperty(index=True, default=None)
    __created_on = DateTimeProperty(default=datetime.now)

    """A relationship to the driver that is assigned to this route. This relationship ensures a 1-1 between driver 
    and route"""
    assigned_to = RelationshipTo(cls_name='routing.models.driver.Driver', rel_type='ASSIGNED_TO', cardinality=One)

    def __init__(self, *args, **kwargs):
        """Creates a new Route.

            Typical usage example:

            route = Route()
        """
        super(Route, self).__init__(*args, **kwargs)
        self.__locations_queue: deque = deque()
        self.__total_duration: float = 0
        self.__total_distance: float = 0
        self.__total_quantity: float = 0
        self.__is_open: bool = True
        self.__departure = None
        self.__stop = None
        self.__tail = None

    @property
    def driver(self):
        """A property to retrieve the driver assign to this route.

        If no driver is assigned, return None.

        @return: The Driver assigned to this route. Otherwise, None.
        """
        try:
            return self.assigned_to.get()
        except DoesNotExist:
            return None

    @property
    def is_open(self) -> bool:
        """A property to determine if this route is open.

        A route is open when new locations can be added to it.

        @return: True if more locations can be added to this route. Otherwise, False.

        """
        return self.__is_open

    @property
    def departure(self) -> Location:
        """A property to get the departure of this route.

        @return: The location representing the departure of this route. If no departure, then return None.
        """
        return self.__departure

    @property
    def last_stop(self) -> Location:
        """A property to get the last location of this route.

        The last location is effectively not the departure.
        @return the last location of this route.
        """
        return self.__locations_queue[-1] if len(self.__locations_queue) > 0 else None

    @property
    def previous(self) -> Location:
        """A property to get the last location of this route.

        The last location is effectively not the departure.
        @return the last location of this route.
        """
        return self.__locations_queue[-1] if len(self.__locations_queue) > 0 else None

    @property
    def total_distance(self) -> float:
        """A property to get the total distance (in miles) to travel this route.

        @return a float representing the total distance to travel this route.
        """
        return self.__total_distance

    @property
    def total_duration(self) -> float:
        """A property to get the total duration (in minutes) to travel this route.

        @return a float representing the total duration to travel this route.
        """
        return self.__total_duration

    @property
    def total_demand(self) -> float:
        """A property to get the total demand of this route.

        @return a float representing the total demand of this route.
        """
        return self.__total_quantity

    @property
    def created_on(self):
        """A property to get the creation datetime of this route.

        @return A datetime object representing the creation datetime of this route.
        """
        return self.__created_on

    @property
    def is_empty(self):
        """A property to determine if this route is empty.

        A route is empty if it contains at a departure, or one location.
        """
        return len(self.__locations_queue) == 0 or len(self.__locations_queue) == 1

    @property
    def itinerary(self):
        """A property to get the path of this route.

        Locations are returned in their order of insertion.

        @return a list representing the locations of this route.
        """
        return list(self.__locations_queue)

    def set_departure(self, departure: Location):
        """Set the departure of this route.

        @param: departure: A location representing the departure of this route.
        """

        self.__departure = copy.deepcopy(departure)

    def add(self, location: Location, pair: Pair) -> bool:
        """Provides the mechanism for add a location this route.

        Add a location ensure the optimal savings. Thus, depending on the location to be inserted, an insertion can be
        appended to the current linked list of inserted between existing locations.

        @return True is addition was successful. Otherwise, return False
        @raise RouteStateException if the departure has not been set.
        """
        if pair and self.__is_open:
            if len(self.__locations_queue) == 0:
                if self.__departure is None:
                    raise RouteStateException('This route has no departure. Set the departure before proceeding.')
                self.__locations_queue.append(self.__departure)
                self.__tail = self.__departure
            if location and (not location.is_assigned):
                if len(self.__locations_queue) == 1:
                    self.__insert_front(location=location)
                elif pair.is_first(location) and not pair.first.is_assigned:
                    logging.info(f'Location {location} is first and head is {self.__departure.next}')
                    if self.__is_exterior(pair.last):
                        logging.info(f'Location {pair.last} is exterior')
                        if pair.last == self.__departure.next:
                            if self.__departure.next.next is None:
                                self.__insert_front(location)
                                logging.info(f'Inserting {location} to the front')
                            else:
                                self.__insert_back(location=location)
                                logging.info(f'Inserting {location} to the back')
                        elif pair.last == self.__tail:
                            self.__insert_front(location=location)
                            logging.info(f'Inserting {location} to the front')
                elif pair.is_last(location) and not pair.last.is_assigned:
                    logging.info(f'Location {location} is last and tail is {self.__tail}')
                    if self.__is_exterior(pair.first):
                        logging.info(f'Location {pair.first} is exterior')
                        if pair.first == self.__departure.next:
                            if self.__departure.next.next is None:
                                self.__insert_front(location)
                                logging.info(f'Inserting {location} to the front')
                            else:
                                self.__insert_back(location)
                                logging.info(f'Inserting {location} to the back')
                        elif pair.first == self.__tail:
                            self.__insert_front(location)
                            logging.info(f'Inserting {location} to the front')
                logging.info('Processing location {} Capacity: {} '
                             'Assigned: {} '
                      .format(location, location.demand, location.is_assigned))
                logging.info('Locations:  {}'.format(self))
                return True
            else:
                if location:
                    logging.info(f'{location} is already assigned.')
            if self.previous == self.__departure:
                self.undo()
        return False if location is None else location.is_assigned

    def __insert_front(self, location: Location):
        """Inserts this location at the beginning of this route.

        Insertion maximizes the savings between locations.

        @param location: Location to insert to the front of this route.
        @raise RouteStateException if the departure has not been set.
        """

        if len(self.__locations_queue) == 0 or self.__departure is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        elif self.__tail.duration(other=location) is None:
            location.is_assigned = False
        else:
            self.__total_duration += self.__tail.duration(other=location)
            self.__total_distance += self.__tail.distance(other=location)
            self.__total_quantity += location.demand

            if len(self.__locations_queue) == 1:
                self.__departure.next = location
                location.previous = self.__departure
            else:
                location.previous = self.__tail
                self.__tail.next = location
            self.__tail = location
            self.__locations_queue.append(location)
            location.is_assigned = True

    def __insert_back(self, location: Location):
        """Insert this location at the end of this route.

        Insertion maximizes the savings between locations.

        @param location: Location to insert to the front of this route.
        @raise RouteStateException if the departure has not been set.
        """

        if len(self.__locations_queue) == 0 or self.__departure is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        elif len(self.__locations_queue) == 1:
            raise RouteStateException('No insertion can\'t be made on the rear.')
        elif self.__departure.distance(location) is None:
            location.is_assigned = False
        else:
            self.__total_duration = (
                    self.__total_duration
                    - self.__departure.duration(self.__departure.next)
                    + self.__departure.duration(location)
                    + self.__departure.next.duration(location)
            )
            self.__total_distance = (
                    self.__total_distance
                    - self.__departure.distance(self.__departure.next)
                    + self.__departure.distance(location)
                    + self.__departure.next.distance(location)
            )
            self.__total_quantity += location.demand
            location.next = self.__departure.next
            self.__departure.next.previous = location
            location.previous = self.__departure
            self.__departure.next = location
            self.__locations_queue.append(location)
            location.is_assigned = True

    def __is_exterior(self, location: Location):
        if len(self.__locations_queue) == 0:
            raise EmptyRouteException('This route is empty')

        return self.__departure.next == location or self.__tail == location

    def undo(self):
        """Removes the last inserted location.

        The last inserted location is the last entry in the deque. It is either the head or the tail of the route.
        """
        if self.previous is not None:
            last_inserted = self.__locations_queue.pop()
            if last_inserted == self.__departure:
                self.__locations_queue.append(last_inserted)
                self.__total_quantity = 0
                self.__total_duration = 0
                self.__total_distance = 0
                self.__tail = self.__departure
            else:
                if last_inserted == self.__departure.next:
                    self.__total_duration -= self.__departure.duration(last_inserted)
                    self.__total_distance -= self.__departure.distance(last_inserted)

                    if last_inserted.next:
                        self.__total_duration = (
                                self.__total_duration
                                - last_inserted.duration(last_inserted.next)
                                + self.__departure.duration(last_inserted.next)
                        )
                        self.__total_distance = (
                                self.__total_distance
                                - last_inserted.distance(last_inserted.next)
                                + self.__departure.distance(last_inserted.next)
                        )

                        last_inserted.next.previous = last_inserted.previous
                    last_inserted.previous.next = last_inserted.next
                elif last_inserted == self.__tail:
                    last_inserted.previous.next = last_inserted.next

                    # Adjust route distance and duration
                    self.__total_duration = (
                            self.__total_duration - self.previous.duration(last_inserted)
                    )
                    self.__total_distance = (
                            self.__total_distance - self.previous.distance(last_inserted)
                    )
                self.__total_quantity -= last_inserted.demand
                self.__tail = last_inserted.previous
                last_inserted.is_assigned = False

    def close_route(self):
        """Provides the mechanism to close this route.

        A route is closed when the last location is effectively the departure.
        """
        if self.__departure and self.__departure.next is None:
            self.__locations_queue = deque()
            self.__departure = None
        elif self.__is_open:
            self.__stop = copy.deepcopy(self.__departure)
            self.__locations_queue.append(self.__stop)
            self.__stop.previous = self.__tail
            self.__tail.next = self.__stop
            self.__stop.next = None
            self.__tail = self.__stop
            self.__stop.is_assigned = True
            self.__is_open = False
            self.__total_duration += self.__tail.duration(self.__stop)
            self.__total_distance += self.__tail.distance(self.__stop)

    def set_total_distance(self):
        """Sets the total distance to travel this route."""
        self.__distance = self.total_distance

    def set_total_duration(self):
        """Sets the total duration to travel this route."""
        self.__duration = self.total_duration

    def set_total_demand(self):
        """Sets the total demand of this route."""
        self.__quantity = self.total_demand

    def serialize(self):
        """Serializes this route.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this route.

                Format:
                {
                    'id': [INTEGER],
                    'created_on': [DATETIME],
                    'total_quantity': [FLOAT],
                    'total_distance': [FLOAT],
                    'total_duration': [FLOAT],
                    'assigned_to': [DRIVER]
                    'itinerary': [LIST_OF_LOCATIONS]
                }

        @return: A JSON object representing this ROUTE.
        """
        itinerary = []
        if not self.is_empty:
            for stop in self.__locations_queue:
                itinerary.append(json.loads(stop.serialize()))

        if self.driver:
            driver = json.loads(self.driver.serialize())
        else:
            driver = None

        obj = json.dumps({
            "id": self.id,
            "created_on": self.__created_on.strftime(constant.DATETIME_FORMAT),
            "total_quantity": self.__total_quantity,
            "total_distance": self.__total_distance,
            "total_duration": self.__total_duration,
            "assigned_to": driver,
            "itinerary": itinerary
        })
        return obj

    def __len__(self):
        return len(self.__locations_queue)

    def __str__(self):
        location = self.__departure
        path = ''
        while location:
            if location.next:
                path += str(location) + ' --> '
            else:
                path += str(location)
            location = location.next
        return path

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        if len(self.__locations_queue) != len(other.__locations_queue):
            return False

        for index in range(len(self.__locations_queue)):
            if self.__locations_queue[index] != other.__locations_queue[index]:
                return False

        return True

    @classmethod
    def category(cls):
        pass

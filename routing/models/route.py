import copy
import json
import os
import sys
from collections import deque
from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty, IntegerProperty, UniqueIdProperty

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing import constant
from routing.models.location import Pair, Location
from routing.exceptions import EmptyRouteException, RouteStateException


class Route(StructuredNode):
    uid = UniqueIdProperty()
    __quantity = FloatProperty(index=True, default=None)
    __distance = FloatProperty(index=True, default=None)
    __duration = FloatProperty(index=True, default=None)
    created_on = DateTimeProperty(default=datetime.now)

    assigned_to = RelationshipTo('routing.models.driver.Driver', 'ASSIGNED_TO')

    def __init__(self, *args, **kwargs):
        super(Route, self).__init__(*args, **kwargs)
        self.locations_queue: deque = deque()
        self.__total_duration: float = 0
        self.__total_distance: float = 0
        self.__total_quantity: float = 0
        self.is_open: bool = True
        self.departure = None
        self.stop = None
        self.tail = None

    @property
    def previous(self):
        return self.locations_queue[-1] if len(self.locations_queue) > 0 else None

    def add(self, location: Location, pair: Pair) -> bool:
        """
        Add a location to route based on insertion rules. Return True is addition was successful, otherwise,
        return False
        """
        if self.is_open:
            if len(self.locations_queue) == 0:
                if self.departure is None:
                    raise RouteStateException('This route has no departure. Set the departure before proceeding.')
                self.locations_queue.append(self.departure)
                # self.departure.is_assigned = True
                self.tail = self.departure
            if location and (not location.is_assigned):
                if len(self.locations_queue) == 1:
                    self.insert_front(location=location)
                elif pair.is_first(location) and not pair.first.is_assigned:
                    print(f'Location {location} is first and head is {self.departure.next}')
                    if self.is_exterior(pair.last):
                        print(f'Location {pair.last} is exterior')
                        if pair.last == self.departure.next:
                            if self.departure.next.next is None:
                                self.insert_front(location)
                                print(f'Inserting {location} to the front')
                            else:
                                self.insert_back(location=location)
                                print(f'Inserting {location} to the back')
                        elif pair.last == self.tail:
                            self.insert_front(location=location)
                            print(f'Inserting {location} to the front')
                elif pair.is_last(location) and not pair.last.is_assigned:
                    print(f'Location {location} is last and tail is {self.tail}')
                    if self.is_exterior(pair.first):
                        print(f'Location {pair.first} is exterior')
                        if pair.first == self.departure.next:
                            if self.departure.next.next is None:
                                self.insert_front(location)
                                print(f'Inserting {location} to the front')
                            else:
                                self.insert_back(location)
                                print(f'Inserting {location} to the back')
                        elif pair.first == self.tail:
                            self.insert_front(location)
                            print(f'Inserting {location} to the front')
                print('\t\t\033[1mProcessing location\033[0m {} \033[1mCapacity:\033[0m {} \033[1mAssigned:\033[0m {}'
                      .format(location, location.demand, location.is_assigned))
                print('\t\t\t\033[1mLocations: \033[0m {}'.format(self))
                return True
            else:
                print(f'{location} is already assigned.')
            if self.previous == self.departure:
                self.undo()
        return False if location is None else location.is_assigned

    def insert_front(self, location: Location):
        """Inserts this location at the beginning of this route.

        This location is inserted after the departure.
        """
        if len(self.locations_queue) == 0 or self.departure is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        else:
            self.__total_duration += self.tail.duration(other=location)
            self.__total_distance += self.tail.distance(other=location)
            self.__total_quantity += location.demand

            if len(self.locations_queue) == 1:
                self.departure.next = location
                location.previous = self.departure
            else:
                location.previous = self.tail
                self.tail.next = location
            self.tail = location
            self.locations_queue.append(location)
            location.is_assigned = True

    def insert_back(self, location: Location):
        """Insert this location at the end of this route."""
        if len(self.locations_queue) == 0 or self.departure is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        elif len(self.locations_queue) == 1:
            raise RouteStateException('No insertion can\'t be made on the rear.')
        else:
            self.__total_duration = (
                    self.__total_duration
                    - self.departure.duration(self.departure.next)
                    + self.departure.duration(location)
                    + self.departure.next.duration(location)
            )
            self.__total_distance = (
                    self.__total_distance
                    - self.departure.distance(self.departure.next)
                    + self.departure.distance(location)
                    + self.departure.next.distance(location)
            )
            self.__total_quantity += location.demand
            location.next = self.departure.next
            self.departure.next.previous = location
            location.previous = self.departure
            self.departure.next = location
            self.locations_queue.append(location)
            location.is_assigned = True

    def is_exterior(self, location: Location):
        if len(self.locations_queue) == 0:
            raise EmptyRouteException('This route is empty')

        return self.departure.next == location or self.tail == location

    def undo(self):
        """Removes last inserted location.

        The last inserted location is the last entry in the deque. It is either the head or the tail of the route.
        """
        if self.previous is not None:
            last_inserted = self.locations_queue.pop()
            if last_inserted == self.departure:
                self.locations_queue.append(last_inserted)
                self.__total_quantity = 0
                self.__total_duration = 0
                self.__total_distance = 0
                self.tail = self.departure
            else:
                if last_inserted == self.departure.next:
                    self.__total_duration -= self.departure.duration(last_inserted)
                    self.__total_distance -= self.departure.distance(last_inserted)

                    if last_inserted.next:
                        self.__total_duration = (
                                self.__total_duration
                                - last_inserted.duration(last_inserted.next)
                                + self.departure.duration(last_inserted.next)
                        )
                        self.__total_distance = (
                                self.__total_distance
                                - last_inserted.distance(last_inserted.next)
                                + self.departure.distance(last_inserted.next)
                        )

                        last_inserted.next.previous = last_inserted.previous
                    last_inserted.previous.next = last_inserted.next
                elif last_inserted == self.tail:
                    last_inserted.previous.next = last_inserted.next

                    # Adjust route distance and duration
                    self.__total_duration = (
                            self.__total_duration - self.previous.duration(last_inserted)
                    )
                    self.__total_distance = (
                            self.__total_distance - self.previous.distance(last_inserted)
                    )
                self.__total_quantity -= last_inserted.demand
                self.tail = last_inserted.previous
                last_inserted.is_assigned = False

    def last_location(self) -> Location:
        return self.locations_queue[-1] if len(self.locations_queue) > 0 else None

    def close_route(self):
        if self.departure and self.departure.next is None:
            self.locations_queue = deque()
            self.departure = None
        elif self.is_open:
            self.stop = copy.deepcopy(self.departure)
            self.locations_queue.append(self.stop)
            self.stop.previous = self.tail
            self.tail.next = self.stop
            self.stop.next = None
            self.tail = self.stop
            self.stop.is_assigned = True
            self.is_open = False
            self.__total_duration += self.tail.duration(self.stop)
            self.__total_distance += self.tail.distance(self.stop)

    def set_total_distance(self):
        self.__distance = self.total_distance

    def set_total_duration(self):
        self.__duration = self.total_duration

    def set_total_demand(self):
        self.__quantity = self.total_demand

    @property
    def total_distance(self):
        return self.__total_distance

    @property
    def total_duration(self):
        return self.__total_duration

    @property
    def total_demand(self):
        return self.__total_quantity

    def get_created_on(self):
        return self.created_on

    def serialize(self):
        obj = json.dumps({
            "id": self.id,
            "created_on": self.created_on.strftime(constant.DATETIME_FORMAT),
            "total_quantity": self.__total_quantity,
            "total_distance": self.__total_distance,
            "total_duration": self.__total_duration,
            "assigned_to": None,
            "itinerary": []
        })
        return obj

    def __len__(self):
        return len(self.locations_queue)

    def __str__(self):
        location = self.departure
        path = ''
        while location:
            if location.next:
                path += str(location) + '\033[1m --> \033[0m'
            else:
                path += str(location)
            location = location.next
        return path

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        if len(self.locations_queue) != len(other.locations_queue):
            return False

        for index in range(len(self.locations_queue)):
            if self.locations_queue[index] != other.locations_queue[index]:
                return False

        return True

    @classmethod
    def category(cls):
        pass

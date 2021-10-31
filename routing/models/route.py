import os
import sys
from collections import deque
from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty, IntegerProperty

working_dir = os.path.abspath(os.path.join('.'))
if working_dir not in sys.path:
    sys.path.append(working_dir)

from routing.managers import LocationManager
from routing.models.location import Location, Pair
from routing.exceptions import EmptyRouteException, RouteStateException


class Route(StructuredNode):
    id = IntegerProperty()
    total_quantity = FloatProperty(index=True)
    total_distance = FloatProperty(index=True)
    total_duration = FloatProperty(index=True)
    created_on = DateTimeProperty(default=datetime.now)

    assigned_to = RelationshipTo('routing.models.driver.Driver', 'ASSIGNED_TO')

    def __init__(self, *args, **kwargs):
        super(Route, self).__init__(*args, **kwargs)
        self.locations_dict = dict()
        self.locations_queue = deque()
        self.departure = None
        self.total_quantity = 0
        self.total_duration = 0
        self.total_distance = 0
        self.previous = self.departure
        self.is_open = True

    def add(self, location: Location, pair: Pair) -> bool:
        """
        Add a location to route based on insertion rules. Return True is addition was successful, otherwise,
        return False
        """
        if self.is_open:
            if len(self.locations_dict) == 0:
                if self.departure is None:
                    raise RouteStateException('This route has no departure. Set the departure before proceeding.')
                self.locations_dict[hex(id(self.departure))] = self.departure
                self.locations_queue.append(self.departure)
                self.departure.is_assigned = True
                self.previous = self.departure
            if location and not location.is_assigned:
                if (pair.is_first(location) or pair.is_last(location)) \
                        and (pair.first() not in self.locations_dict and pair.last() not in self.locations_dict):
                    self.update_properties(location=location, previous=self.previous)
                    self.locations_queue.append(location)
                elif pair.is_first(location):
                    if self.is_exterior(pair.last()):
                        self.update_properties(location=location, previous=pair.last())
                        self.locations_queue.append(location)
                elif pair.is_last(location):
                    if self.is_exterior(pair.first()):
                        self.update_properties(location=location, previous=pair.first())
                        self.locations_queue.append(location)
                return True
            if self.previous == self.departure:
                self.undo()
        return False if location is None else location.is_assigned

    def update_properties(self, location: Location, previous: Location):
        self.total_duration += LocationManager.get_duration(location1=previous, location2=location)
        self.total_distance += LocationManager.get_distance(location1=previous, location2=location)
        self.total_quantity += location.demand
        self.locations_dict[hex(id(location))] = location
        location.previous = self.locations_dict[hex(id(previous))]
        self.locations_dict[hex(id(previous))].next = location
        self.previous = location
        location.is_assigned = True

    def is_exterior(self, location: Location):
        if len(self.locations_dict) == 0:
            raise EmptyRouteException('This route is empty')
        if len(self.locations_dict) == 1 and (self.locations_dict[0] == self.departure or self.locations_dict[0] == self.departure):
            return True
        elif len(self.locations_dict) > 1:
            return self.locations_dict[1] == location or self.locations_dict[-1] == location

    def undo(self):
        """
        Remove last inserted location
        """
        if self.previous is not None:
            last_inserted = self.locations_queue.pop()
            self.locations_dict[hex(id(last_inserted))].previous.next = self.locations_dict[hex(id(last_inserted))].next
            self.previous = self.locations_queue.pop()
            self.locations_queue.append(self.previous)
            self.total_quantity -= last_inserted.demand
            self.total_duration -= LocationManager.get_duration(location1=self.previous, location2=last_inserted)
            self.total_distance -= LocationManager.get_distance(location1=self.previous, location2=last_inserted)
            del self.locations_dict[hex(id(last_inserted))]

    def last_location(self) -> Location:
        return self.previous

    def close_route(self):
        self.locations_dict.append(self.departure)
        self.is_open = False

    def get_total_distance(self):
        return self.total_distance

    def get_total_duration(self):
        return self.total_duration

    def get_total_demand(self):
        return self.total_quantity

    def get_created_on(self):
        return self.created_on

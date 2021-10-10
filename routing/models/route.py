import os
import sys
from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty, IntegerProperty

working_dir = os.path.abspath(os.path.join('.'))
if working_dir not in sys.path:
    sys.path.append(working_dir)

from routing.managers import LocationManager
from routing.models.location import Location, Pair


class Route(StructuredNode):
    id = IntegerProperty()
    total_quantity = FloatProperty(index=True)
    total_distance = FloatProperty(index=True)
    total_duration = FloatProperty(index=True)
    created_on = DateTimeProperty(default=datetime.now)

    assigned_to = RelationshipTo('routing.models.driver.Driver', 'ASSIGNED_TO')

    def __init__(self, departure: Location, *args, **kwargs):
        super(Route, self).__init__(args, kwargs)
        self.locations = list()
        self.locations.append(departure)
        self.departure = departure
        self.total_quantity = 0
        self.total_duration = 0
        self.total_distance = 0
        self.previous = self.departure

    def add(self, location: Location):
        if location and not location.is_assigned:
            self.locations.append(location)
            location.is_assigned = True
            self.total_duration += LocationManager.get_duration(location1=self.previous, location2=location)
            self.total_distance += LocationManager.get_distance(location1=self.previous, location2=location)
            self.total_quantity += location.demand
            self.previous = location
            location.is_assigned = True
            return True
        return False

    def insert(self, pair: Pair):
        if len(self.locations) == 1:
            for location in pair.get_pair():
                self.add(location)
        elif pair.get_first() and pair.get_second():
            location1, location2 = pair.get_pair()
            if (location1 in self.locations ^ location2 in self.locations) and pair.is_assignable():
                if location1 in self.locations and not location1.is_interior(self) and not location2.is_assigned:
                    self.add(location2)
                elif location2 in self.locations and not location2.is_interior(self) and not location1.is_assigned:
                    self.add(location1)

    # def is_interior(self, route: routing.models.route.Route):
    #     if route is None or len(route.locations) < 3:
    #         return False
    #
    #     return self not in route.locations[1:len(route.locations) - 1]

    def close_route(self):
        self.locations.append(self.departure)
        return True

    def get_total_distance(self):
        pass

    def set_total_distance(self):
        pass

    def get_total_duration(self):
        pass

    def set_total_duration(self):
        pass

    def get_driver(self):
        pass

    def get_total_demand(self):
        pass

    def get_created_on(self):
        return self.created_on

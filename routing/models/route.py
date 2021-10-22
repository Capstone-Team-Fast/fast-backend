import os
import sys
from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty, IntegerProperty

working_dir = os.path.abspath(os.path.join('.'))
if working_dir not in sys.path:
    sys.path.append(working_dir)

from routing.managers import LocationManager
from routing.models.location import Location


class Route(StructuredNode):
    id = IntegerProperty()
    total_quantity = FloatProperty(index=True)
    total_distance = FloatProperty(index=True)
    total_duration = FloatProperty(index=True)
    created_on = DateTimeProperty(default=datetime.now)

    assigned_to = RelationshipTo('routing.models.driver.Driver', 'ASSIGNED_TO')

    def __init__(self, departure: Location, *args, **kwargs):
        super(Route, self).__init__(*args, **kwargs)
        self.locations = list()
        self.locations.append(departure)
        self.departure = departure
        self.total_quantity = 0
        self.total_duration = 0
        self.total_distance = 0
        self.previous = self.departure
        self.is_open = True

    def add(self, location: Location):
        if self.is_open and location and not location.is_assigned:
            self.locations.append(location)
            location.is_assigned = True
            self.total_duration += LocationManager.get_duration(location1=self.previous, location2=location)
            self.total_distance += LocationManager.get_distance(location1=self.previous, location2=location)
            self.total_quantity += location.demand
            self.previous = location
            location.is_assigned = True
            return True
        return False

    def close_route(self):
        self.locations.append(self.departure)
        self.is_open = False

    def get_total_distance(self):
        return self.total_distance

    def get_total_duration(self):
        return self.total_duration

    def get_total_demand(self):
        return self.total_quantity

    def get_driver(self):
        return None

    def assign_to(self):
        return None

    def get_created_on(self):
        return self.created_on

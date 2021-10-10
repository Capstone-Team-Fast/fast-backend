from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty

# Add serializers
from routing.managers import LocationManager
from routing.models.location import Location


class Route(StructuredNode):
    # Add id to different model
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
        if len(self.locations) == 1 and not location.is_assigned:
            self.locations.append(location)
            location.is_assigned = True
            self.total_duration += LocationManager.get_duration(location1=self.previous, location2=location)
            self.total_distance += LocationManager.get_distance(location1=self.previous, location2=location)
            self.total_quantity += location.demand
            self.previous = location


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

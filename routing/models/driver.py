import os
import sys
from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo

working_dir = os.path.abspath(os.path.join('.'))
if working_dir not in sys.path:
    sys.path.append(working_dir)

for p in sys.path:
    print(p)

from routing.models.route import Route
from routing.models.location import Location, Pair


class Driver(StructuredNode):
    ROLES = {'P': 'Employee', 'V': 'Volunteer'}

    uid = UniqueIdProperty()
    first_name = StringProperty(index=True, required=True)
    last_name = StringProperty(index=True, required=True)
    employee_status = StringProperty(index=True, choices=ROLES, required=True)
    phone = StringProperty(index=True)
    capacity = IntegerProperty(default=0)
    start_time = DateTimeProperty()
    end_time = DateTimeProperty()
    created_on = DateTimeProperty(default=datetime.now)
    modified_on = DateTimeProperty(default_now=True)

    serves = RelationshipTo('routing.models.location.Location', 'SERVES')
    is_available_on = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')
    speaks = RelationshipTo('routing.models.language.Language', 'SPEAKS')

    def __init__(self, *args, **kwargs):
        super(Driver, self).__init__(*args, **kwargs)
        self.route = Route()
        self.route.departure = None

    def set_departure(self, depot: Location):
        self.route.departure = depot

    def get_departure(self):
        return self.route.departure

    def add(self, pair: Pair) -> bool:
        """
        Add pair to route. Return True is addition was successful, otherwise, return False
        """
        # Check capacity constraint as well as duration constraint before appending new locations
        # Insertion of new locations is handled by Route.insert()
        if self.route.is_open:
            for location in pair.get_pair():
                if not self.route.add(location=location, pair=pair):
                    return False
                if self.route.total_duration <= self.end_time - self.start_time \
                        and self.route.total_quantity <= self.capacity:
                    return True
                if self.route.total_duration > self.end_time - self.start_time:  # Check DateTime operation
                    self.route.undo()
                    self.route.close_route()
                elif self.route.total_quantity > self.capacity:
                    self.route.undo()
                    self.route.close_route()
        return False

    def get_availability(self, location: Location):
        """
        Get the availability of this driver with respect to a location. In other words,
        can this drive deliver to this location?
        """
        self.speaks.relationship.values()

    def __hash__(self):
        return hash((self.first_name, self.last_name, self.employee_status))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.first_name == other.first_name and self.last_name == other.last_name
                and self.employee_status == other.employee_status)

    def __str__(self):
        return '{},{}'.format(self.last_name, self.first_name)

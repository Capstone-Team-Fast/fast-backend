import copy
import enum
import json
import math
import os
import sys
from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing.models.location import Pair, Depot
from routing.models.route import Route


class Driver(StructuredNode):
    """Define a Driver node with its properties.

    This node represents a driver object used in the graph database. This object defines various methods for
    querying the graph database for a particular instance of Driver.

    """

    class Role(enum.Enum):
        """Define the Role of a driver within the organization that this driver serves."""
        EMPLOYEE = 'P'
        VOLUNTEER = 'V'

    ROLES = {Role.EMPLOYEE.value: Role.EMPLOYEE.name, Role.VOLUNTEER.value: Role.VOLUNTEER.name}

    uid = UniqueIdProperty()
    external_id = IntegerProperty(required=False, unique_index=True)
    first_name = StringProperty(index=True, required=True)
    last_name = StringProperty(index=True, required=True)
    employee_status = StringProperty(index=True, choices=ROLES, required=True)
    phone = StringProperty(index=True)
    capacity = IntegerProperty(default=0)
    start_time = DateTimeProperty(default_now=True)
    end_time = DateTimeProperty()
    max_delivery = IntegerProperty(default=None)
    created_on = DateTimeProperty(default=datetime.now)
    modified_on = DateTimeProperty(default_now=True)

    serves = RelationshipTo('routing.models.location.Customer', 'SERVES')
    is_available_on = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')
    language = RelationshipTo('routing.models.language.Language', 'SPEAKS')

    def __init__(self, *args, **kwargs):
        super(Driver, self).__init__(*args, **kwargs)
        self.__route = Route()
        self.__route.set_departure(None)
        self.__is_saved = False

    def save_route(self):
        self.__route.save()
        self.__route.set_total_demand()
        self.__route.set_total_distance()
        self.__route.set_total_duration()
        self.__route.assigned_to.connect(self)
        self.__is_saved = True

    def reset(self):
        self.__route = Route()
        self.__route.set_departure(None)

    def set_departure(self, depot: Depot):
        self.__route.set_departure(depot)

    @property
    def route(self) -> Route:
        if not self.__is_saved:
            self.save_route()
        return self.__route

    @property
    def departure(self) -> Depot:
        return self.__route.departure

    def add(self, pair: Pair) -> bool:
        """Add a Pair of Location to the Route assigned to this driver.

        Args:
            pair: A Pair of Locations.

        Return:
            True if addition was successful, otherwise, return False
        """
        # Add constraint for delivery limit for volunteers
        # Check capacity constraint as well as duration constraint before appending new locations
        # Insertion of new locations is handled by Route.insert()
        if self.__route.is_open:
            for location in pair.get_pair():
                if not self.__route.add(location=location, pair=pair):
                    return False

                cumulative_duration_minutes = math.trunc(self.__route.total_duration)
                cumulative_duration_seconds = self.__route.total_duration - cumulative_duration_minutes
                cumulative_duration = cumulative_duration_minutes * 60 + cumulative_duration_seconds
                if (cumulative_duration < (self.end_time - self.start_time).total_seconds()) \
                        and (self.__route.total_demand < self.capacity):
                    if self.max_delivery:
                        if len(self.__route) - 1 == self.max_delivery:
                            return False
                    else:
                        continue
                elif cumulative_duration == (self.end_time - self.start_time).total_seconds():
                    print(f'\nDriver has met allocated time.')
                elif self.__route.total_demand == self.capacity:
                    print(f'\nDriver is at capacity.')
                elif cumulative_duration > (self.end_time - self.start_time).total_seconds():
                    print(f'Inserting this location lead to overtime. Undoing insertion.')
                    self.__route.undo()
                    print(f'\nUndid insertion of {location}')
                elif self.__route.total_demand > self.capacity:
                    print(f'\nRoute is overcapacity.')
                    self.__route.undo()
                    print(f'\nUndid insertion of {location}')

            return pair.first.is_assigned and pair.last.is_assigned
        return False

    def get_languages(self):
        return self.language.all()

    def get_availability(self):
        """
        Get the availability of this driver with respect to a location. In other words,
        can this drive deliver to this location?
        """
        return self.is_available_on.all()

    def __hash__(self):
        return hash((self.first_name, self.last_name, self.employee_status))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.first_name == other.first_name and self.last_name == other.last_name
                    and self.employee_status == other.employee_status and self.external_id == other.external_id)
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{},{}'.format(self.last_name, self.first_name)

    def is_volunteer(self):
        return self.employee_status == Driver.Role.VOLUNTEER.value

    def is_full_time(self):
        return self.employee_status == Driver.Role.EMPLOYEE.value

    def serialize(self):
        availabilities = self.get_availability()
        if availabilities:
            availabilities.sort()
            availabilities = [json.loads(availability.serialize()) for availability in availabilities]
        else:
            availabilities = []

        languages = self.get_languages()
        if languages:
            languages.sort()
            languages = [json.loads(language.serialize()) for language in languages]
        else:
            languages = []

        obj = json.dumps({
            'id': self.external_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'capacity': self.capacity,
            'employee_status': self.employee_status,
            'delivery_limit': self.max_delivery,
            'availability': availabilities,
            'languages': languages,
        })
        return obj

    @classmethod
    def category(cls):
        pass

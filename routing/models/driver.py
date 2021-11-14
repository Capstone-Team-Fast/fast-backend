import copy
import enum
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
    start_time = DateTimeProperty()
    end_time = DateTimeProperty()
    created_on = DateTimeProperty(default=datetime.now)
    modified_on = DateTimeProperty(default_now=True)

    serves = RelationshipTo('routing.models.location.Customer', 'SERVES')
    is_available_on = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')
    language = RelationshipTo('routing.models.language.Language', 'SPEAKS')

    def __init__(self, *args, **kwargs):
        super(Driver, self).__init__(*args, **kwargs)
        self.__route = Route()
        self.__route.departure = None

    def reset(self):
        self.__route = Route()
        self.__route.departure = None

    def set_departure(self, depot: Depot):
        self.__route.departure = copy.deepcopy(depot)

    @property
    def route(self) -> Route:
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
                        and (self.__route.total_quantity < self.capacity):
                    continue
                elif cumulative_duration == (self.end_time - self.start_time).total_seconds():
                    print(f'\nDriver has met allocated time.')
                elif self.__route.total_quantity == self.capacity:
                    print(f'\nDriver is at capacity.')
                elif cumulative_duration > (self.end_time - self.start_time).total_seconds():
                    print(f'Inserting this location lead to overtime. Undoing insertion.')
                    self.__route.undo()
                    print(f'\nUndid insertion of {location}')
                elif self.__route.total_quantity > self.capacity:
                    print(f'\nRoute is overcapacity.')
                    self.__route.undo()
                    print(f'\nUndid insertion of {location}')
            return pair.first.is_assigned and pair.last.is_assigned
        return False

    def get_availability(self):
        """
        Get the availability of this driver with respect to a location. In other words,
        can this drive deliver to this location?
        """
        return self.language.all()

    def __hash__(self):
        return hash((self.first_name, self.last_name, self.employee_status))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return (self.first_name == other.first_name and self.last_name == other.last_name
                    and self.employee_status == other.employee_status)
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{},{}'.format(self.last_name, self.first_name)

    def is_volunteer(self):
        return self.employee_status == Driver.Role.VOLUNTEER.value

    def is_full_time(self):
        return self.employee_status == Driver.Role.EMPLOYEE.value

    def serialize(self):
        # {
        #     "id": 6,
        #     "user": 6,
        #     "capacity": 5,
        #     "employee_status": "employee",
        #     "phone": "123-123-4567",
        #     "availability": {
        #         "id": 2,
        #         "sunday": true,
        #         "monday": false,
        #         "tuesday": true,
        #         "wednesday": true,
        #         "thursday": false,
        #         "friday": true,
        #         "saturday": false
        #     },
        #     "languages": []
        # }
        pass

    @classmethod
    def category(cls):
        pass

import enum
import json
import math
import os
import sys
from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, \
    RelationshipTo, AttemptedCardinalityViolation

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing.models.location import Pair, Depot
from routing.models.route import Route


class Driver(StructuredNode):
    """This class defines a Driver node with its properties.

    This node represents a driver object used in the graph database. This object defines various methods for
    querying the graph database for a particular instance of Driver.

        Typical usage example:

        foo = Driver(external_id=1, first_name='John', last_name='Doe', capacity=35, employee_status='P')
        foo = Driver(first_name='John', last_name='Doe', capacity=35, employee_status='V')

        Note that external_id is not required. employee_status can be either 'P' or 'V'.
    """

    class Role(enum.Enum):
        """Define the Role of a driver within the organization that this driver serves.

        Two values are possible. 'P', which refers to 'PERMANENT' and 'V', which refers to 'VOLUNTEER'.
        """
        EMPLOYEE = 'P'
        VOLUNTEER = 'V'

    __ROLES = {Role.EMPLOYEE.value: Role.EMPLOYEE.name, Role.VOLUNTEER.value: Role.VOLUNTEER.name}

    """A unique id assigned upon creating this object"""
    uid = UniqueIdProperty()

    """An integer representing the id of this driver."""
    external_id = IntegerProperty(required=False, unique_index=True)

    """A string representing the firstname of this driver."""
    first_name = StringProperty(index=True, required=True)

    """A string representing the lastname of this driver."""
    last_name = StringProperty(index=True, required=True)

    """A character representing the role of this driver. It is 'P', for 'PERMANENT' or 'V', for 'VOLUNTEER'."""
    employee_status = StringProperty(index=True, choices=__ROLES, required=True)

    """An integer representing the capacity of the vehicle driven by this driver."""
    capacity = IntegerProperty(default=0)

    """A datetime object representing the starting time for this driver's schedule."""
    start_time = DateTimeProperty(default_now=True)

    """A datetime object representing the ending time for this driver's schedule."""
    end_time = DateTimeProperty()

    """An integer representing the maximum number of addresses this driver can deliver to. 
    
    This number does not include the departure and finishing location. By default, is value is None.
    """
    max_delivery = IntegerProperty(default=None)

    """An integer representing the maximum number of addresses this driver can deliver to."""
    created_on = DateTimeProperty(default=datetime.now)

    """A datetime object representing the last modified datetime of this driver."""
    modified_on = DateTimeProperty(default_now=True)

    """A relationship to location this driver serves."""
    serves = RelationshipTo('routing.models.location.Customer', 'SERVES')

    """A relationship to the day when this driver is available."""
    is_available_on = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')

    """A relationship to the language this drives speaks."""
    language = RelationshipTo('routing.models.language.Language', 'SPEAKS')

    def __init__(self, *args, **kwargs):
        """Creates a Driver and assigns it a Route. Its departure is set to None by default.

            Typical usage example:

            driver = Driver(external_id=1, first_name='John', last_name='Doe', capacity=35, employee_status='P')
            driver = Driver(first_name='John', last_name='Doe', capacity=35, employee_status='V')
        """
        super(Driver, self).__init__(*args, **kwargs)
        self.__route = Route()
        self.__route.set_departure(None)
        self.__is_saved = False

    def __save_route(self):
        """Provides the mechanism for persisting the route assigned to this driver.

        This operation sets the following  properties:
            * Total demand: Cumulative demand of the location of this route
            * Total distance: Cumulative distance traveled for visiting all the locations of this route in the order
                specified. The distance is measured in miles.
            * Total duration: Cumulative duration for visiting all the locations of this route in the order  specified.
                The duration is measured in minutes.
        """
        self.__route.save()
        self.__route.set_total_demand()
        self.__route.set_total_distance()
        self.__route.set_total_duration()
        try:
            self.__route.assigned_to.connect(self)
        except AttemptedCardinalityViolation:
            self.__route.assigned_to.reconnect(self, self)
        self.__is_saved = True

    def reset(self):
        """Provides the mechanism for creating a new route for this driver.

        If a route was assigned to this driver, the previous relationship is deleted and replace with a new one. Upon
        creation, the departure of this route is set to None.
        """
        self.__route = Route().save()
        try:
            self.__route.assigned_to.connect(self)
        except AttemptedCardinalityViolation:
            self.__route.assigned_to.reconnect(self, self)
        self.__route.set_departure(None)

    def set_departure(self, depot: Depot):
        """Provides the mechanism for setting the departure of this driver's route."""
        self.__route.set_departure(depot)

    @property
    def route(self) -> Route:
        """Property for retrieving this driver's route."""
        if not self.__is_saved:
            self.__save_route()
        return self.__route

    @property
    def departure(self) -> Depot:
        """Property for retrieving the departure of this route."""
        return self.__route.departure

    def add(self, pair: Pair) -> bool:
        """Provides the mechanism for adding a Pair of Location to the Route assigned to this driver.

        This implementation validates the capacity and duration constraints. It handles maximum delivery constraint
            specific to Volunteers

        @param: pair: A Pair of Locations to insert
        @return: True if the locations of this pair are assigned. Otherwise, return False. When, A value of True does
            not necessarily mean that the two locations are assigned to the same driver, this driver.
        """
        if self.__route.is_open:
            for location in pair.get_pair():
                if not self.__route.add(location=location, pair=pair):
                    return False

                cumulative_duration_minutes = math.trunc(self.__route.total_duration)
                cumulative_duration_seconds = self.__route.total_duration - cumulative_duration_minutes
                cumulative_duration = cumulative_duration_minutes * 60 + cumulative_duration_seconds
                if (cumulative_duration < (self.end_time - self.start_time).total_seconds()) \
                        and (self.__route.total_demand < float(str(self.capacity))):
                    if self.max_delivery:
                        if len(self.__route) - 1 == self.max_delivery:
                            print(f'\nVolunteer reached delivery limit.\n')
                            self.__route.close_route()
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
                elif self.__route.total_demand > int(str(self.capacity)):
                    print(f'\nRoute is overcapacity.')
                    self.__route.undo()
                    print(f'\nUndid insertion of {location}')

            return pair.first.is_assigned and pair.last.is_assigned
        return False

    def get_languages(self):
        """List of languages spoken by this driver.

        @return a list of Language objects representing the languages spoken by this driver.
        """
        return self.language.all()

    def get_availability(self):
        """Get the availability of this driver.

        @return a list of Availability objects representing when this driver is available.
        """
        return self.is_available_on.all()

    def is_volunteer(self):
        """Checks if this driver is a volunteer.

        @return True if this driver is a volunteer. Otherwise, False.
        """
        return self.employee_status == Driver.Role.VOLUNTEER.value

    def is_full_time(self):
        """Checks if this driver is a full-time employer.

        @return True if this driver is a full-time (permanent) employee. Otherwise, False.
        """
        return self.employee_status == Driver.Role.EMPLOYEE.value

    def serialize(self):
        """Serializes this driver.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this driver.

                Format:
                {
                    'id': [INTEGER],
                    'first_name': [STRING],
                    'last_name': [STRING],
                    'capacity': [INTEGER],
                    'employee_status': [CHARACTER],
                    'delivery_limit': [INTEGER]
                    'availability': []
                    'languages': []
                }

        @return: A JSON object representing this DRIVER.
        """
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
            'languages': languages
        })
        return obj

    @classmethod
    def category(cls):
        pass

    def __hash__(self):
        return hash((self.first_name, self.last_name, self.employee_status))

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return (self.first_name == other.first_name and self.last_name == other.last_name
                    and self.employee_status == other.employee_status and self.external_id == other.external_id)
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{},{}'.format(self.last_name, self.first_name)

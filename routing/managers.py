import enum
from heapq import heappop

import neomodel

from routing.exceptions import RouteStateException
from routing.models.location import Location, Pair
from routing.services import BingGeocodeService, BingMatrixService


class DriverManager:
    def __init__(self):
        self.drivers = list()


class LocationManager:
    depot: Location = None
    locations = set()
    connection: str = ''

    def __init__(self, db_connection: neomodel.db, depot: Location):
        self.depot = depot
        self.connection = db_connection
        LocationManager.depot = depot
        LocationManager.add(LocationManager.depot)
        LocationManager.connection = db_connection

    @staticmethod
    def remove(location: Location):
        if len(LocationManager.locations) == 0:
            raise StopIteration
        if not isinstance(location, Location):
            raise ValueError(f'Type {type(location)} not supported.')
        LocationManager.locations.remove(location)

    @staticmethod
    def get_locations() -> list:
        return list(LocationManager.locations)

    @staticmethod
    def add(location: Location):
        """Add the location argument to the graph database.

        This method ensures that a location, by the time it is added to the graph database, has its coordinates set.
        The coordinates consist of a latitude and a longitude.
        """
        if location and location not in LocationManager.locations:
            if location in Location.nodes.all():
                location = Location.nodes.get(address__iexact=location.address, city__iexact=location.city,
                                              state__iexact=location.state, zipcode__exact=location.zipcode,
                                              is_center=location.is_center)
            if location.latitude is None or location.longitude is None:
                print(f'\nRetrieving geocode for location {location}\n')
                location.latitude, location.longitude = BingGeocodeService.get_geocode(location=location)
                location = location.save()

            if not BingMatrixService.build_matrices(start=location, end=list(LocationManager.locations)):
                print(f'Failed to build matrix between {location} and {LocationManager.locations}')
            print(f'Added new location {location}')
            LocationManager.locations.add(location)
            print(f'LocationManager State {LocationManager.locations}\n')

    @staticmethod
    def add_collection(locations: list):
        """Adds this list of locations to the graph database.

        If locations is None, no change occurs. Otherwise, each location in this list is added to the graph
        database.
        """
        if locations:
            for location in locations:
                if len(LocationManager.locations) == 0:
                    LocationManager.add(location)
                else:
                    if location not in LocationManager.locations:
                        LocationManager.add(location)

    @staticmethod
    def get_distance(location1: Location, location2: Location):
        """Gets the distance (in meters) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if location1 is None or location2 is None:
            return 0.0

        if location1 == location2:
            return 0.0

        if location1 in LocationManager.locations and location2 in LocationManager.locations:
            return location1.neighbor.relationship(location2).distance

        if location1 not in LocationManager.locations:
            LocationManager.add(location1)

        if location2 not in LocationManager.locations:
            LocationManager.add(location2)

        return location1.neighbor.relationship(location2).distance

    @staticmethod
    def get_duration(location1: Location, location2: Location):
        """Gets the duration (in minutes) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if location1 is None or location2 is None:
            return 0.0

        if location1 == location2:
            return 0.0

        if location1 in LocationManager.locations and location2 in LocationManager.locations:
            return location1.neighbor.relationship(location2).duration

        if location1 not in LocationManager.locations:
            LocationManager.add(location1)

        if location2 not in LocationManager.locations:
            LocationManager.add(location2)
        return location1.neighbor.relationship(location2).duration

    @staticmethod
    def get_distance_savings(location1: Location, location2: Location):
        """Gets the savings (in meters) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if LocationManager.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if LocationManager.depot in LocationManager.locations and location1 in LocationManager.locations \
                and location2 in LocationManager.locations:
            return LocationManager.__get_distance_saved(location1, location2)
        if LocationManager.depot not in LocationManager.locations:
            LocationManager.add(LocationManager.depot)
        if location1 not in LocationManager.locations:
            LocationManager.add(location1)
        if location2 not in LocationManager.locations:
            LocationManager.add(location2)
        return LocationManager.__get_distance_saved(location1, location2)

    @staticmethod
    def get_duration_savings(location1: Location, location2: Location):
        """Gets the savings (in meters) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if LocationManager.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if LocationManager.depot in LocationManager.locations and location1 in LocationManager.locations \
                and location2 in LocationManager.locations:
            return LocationManager.__get_duration_saved(location1, location2)
        if LocationManager.depot not in LocationManager.locations:
            LocationManager.add(LocationManager.depot)
        if location1 not in LocationManager.locations:
            LocationManager.add(location1)
        if location2 not in LocationManager.locations:
            LocationManager.add(location2)
        return LocationManager.__get_duration_saved(location1, location2)

    @staticmethod
    def size():
        """Gets the number of locations being currently managed."""
        return len(LocationManager.locations)

    @staticmethod
    def __get_distance_saved(location1: Location, location2: Location):
        """Computes the savings distance between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        LocationManager.__validate_link(location1, location2)

        return (LocationManager.depot.neighbor.relationship(location1).distance
                + LocationManager.depot.neighbor.relationship(location2).distance
                - location1.neighbor.relationship(location2).distance)

    @staticmethod
    def __get_duration_saved(location1: Location, location2: Location):
        """Computes the savings duration between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        LocationManager.__validate_link(location1, location2)

        return (LocationManager.depot.neighbor.relationship(location1).duration
                + LocationManager.depot.neighbor.relationship(location2).duration
                - location1.neighbor.relationship(location2).duration)

    @staticmethod
    def __validate_link(location1: Location, location2: Location):
        """This helper function ensures that there is an edge between the two locations.

        This implementation guarantees that there is an edge between any two locations.
        """
        if (location1 and location2) and (location1 != location2):
            if LocationManager.depot is None:
                raise RouteStateException('This route has no departure. Set the departure before proceeding.')
            if LocationManager.depot.neighbor.relationship(location1) is None:
                BingMatrixService.build_matrices(start=LocationManager.depot, end=[location1])
                # raise RelationshipError(
                #     'There is no link between node \'{}\' and node \'{}\''.format(LocationManager.depot, location1))
            if LocationManager.depot.neighbor.relationship(location2) is None:
                BingMatrixService.build_matrices(start=LocationManager.depot, end=[location2])
                # raise RelationshipError(
                #     'There is no link between node \'{}\' and node \'{}\''.format(LocationManager.depot, location2))
            if location1.neighbor.relationship(location2) is None:
                BingMatrixService.build_matrices(start=location1, end=[location2])
                # raise RelationshipError('There is no link between node \'{}\' and node \'{}\''
                #                         .format(location1, location2))


class SavingsManager:
    def __init__(self, db_connection: str, depot: Location, locations: list):
        self.depot = depot
        self.__location_manager = LocationManager(db_connection=db_connection, depot=depot)
        self.__heap = self.__heapify(locations=locations)

    def __heapify(self, locations: list):
        heap = []
        if locations:
            pairs = []
            savings_dictionary = {}
            index = 0
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    if locations[i] != locations[j]:
                        pair = Pair(locations[i], locations[j])
                        saving = self.__location_manager.get_distance_savings(location1=pair.location1,
                                                                              location2=pair.location2)
                        savings_dictionary[saving] = index
                        pairs.append(pair)
                        index += 1

            savings_dictionary = sorted(savings_dictionary.items(), key=lambda x: x[0])
            for _, index in savings_dictionary:
                heap.append(pairs[index])
        return heap

    def __next__(self):
        if self.__heap:
            return self.__heap.pop()
        raise StopIteration

    def __iter__(self):
        return self


class RouteManager:
    """
    Uses constraints to build routes and assign them to drivers
    """

    class _State(enum.Enum):
        IDLE = 0
        HARD_SOLVING = 1
        SOFT_SOLVING = 2
        SOLVED = 3
        INFEASIBLE = 4

    class _Alphabet(enum.Enum):
        FALSE = 0
        TRUE = 1
        DONE = 2

    def __init__(self, db_connection: str, depot: Location, drivers: list, locations: list,
                 prioritize_volunteer: bool = False):
        self.drivers = drivers
        self.locations = locations
        self.location_manager = LocationManager(db_connection=db_connection, depot=depot)
        self.location_manager.add_collection(locations=locations)
        self.savings_manager = SavingsManager(db_connection=db_connection, depot=depot, locations=locations)
        self.prioritize_volunteer = prioritize_volunteer
        self.drivers_heap = self.build_driver_heap()

    def build_driver_heap(self):
        drivers_heap = []
        if self.drivers:
            # Build a dictionary of driver's index: driver's capacity
            driver_dictionary = {index: driver.capacity for index, driver in enumerate(self.drivers)}
            driver_dictionary = sorted(driver_dictionary.items(), key=lambda x: x[1], reverse=True)

            if self.prioritize_volunteer:
                volunteers = []
                employees = []
                for index, driver_capacity in driver_dictionary:
                    if self.drivers[index].is_volunteer():
                        volunteers.append(self.drivers)
                    elif self.drivers[index].is_fulltime():
                        employees.append(self.drivers)
                drivers_heap.extend(volunteers)
                drivers_heap.extend(employees)
            else:
                for index, driver_capacity in driver_dictionary:
                    drivers_heap.append(self.drivers[index])
        return drivers_heap

    def build_routes(self):
        assigned_locations_set = set()
        if self.savings_manager:
            for pair in self.savings_manager:
                print(f'\n\033[1m Processing pair\033[0m ({pair.first}, {pair.last})')
                for driver in self.drivers_heap:
                    print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                    if driver.get_departure() is None:
                        driver.set_departure(self.location_manager.depot)
                    if driver.route.is_open and driver.add(pair=pair):
                        break
                if pair.is_assignable():
                    print(f'{RouteManager._State.INFEASIBLE}')
                if pair.first.is_assigned:
                    assigned_locations_set.add(pair.first)
                if pair.last.is_assigned:
                    assigned_locations_set.add(pair.last)
                if len(assigned_locations_set) == len(self.locations):
                    break

            for driver in self.drivers_heap:
                if len(driver.route) <= 1:
                    driver.route.departure = None
                    driver.route = None
                elif len(driver.route) > 1 and driver.route.is_open:
                    driver.route.close_route()
            return RouteManager._State.SOLVED

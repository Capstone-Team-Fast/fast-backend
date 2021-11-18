import copy
import enum
import heapq
import json
import sys

import neomodel

from routing.exceptions import RouteStateException
from routing.models.location import Address, Pair, Location
from routing.services import BingGeocodeService, BingMatrixService


class DriverManager:
    def __init__(self):
        self.drivers = list()


class LocationManager:
    def __init__(self, db_connection: neomodel.db, depot: Location):
        self.__depot = depot
        self.__connection = db_connection
        self.__locations = set()
        self.__addresses = dict()

    @property
    def depot(self):
        return self.__depot

    @property
    def connection(self):
        return self.__connection

    @property
    def locations(self) -> list:
        return list(self.__locations)

    @property
    def size(self):
        """Gets the number of locations being currently managed."""
        return len(self.__locations)

    def remove(self, location: Location):
        if len(self.__locations) == 0:
            raise StopIteration
        if not isinstance(location, Location):
            raise ValueError(f'Type {type(location)} not supported.')
        self.__locations.remove(location)
        if self.__addresses.get(location.address):
            self.__addresses[location.address] -= 1
            if self.__addresses[location.address] == 0:
                del self.__addresses[location.address]

    def add(self, location: Location):
        """Add the location argument to the graph database.

        This method ensures that a location, by the time it is added to the graph database, has its coordinates set.
        The coordinates consist of a latitude and a longitude.
        """
        if location:
            if location not in self.__locations:
                if location not in Location.nodes.all():
                    location.save()

                address = location.address
                if address and (address.latitude is None or address.longitude is None):
                    print(f'\nRetrieving geocode for location {address}\n')
                    address.latitude, address.longitude = BingGeocodeService.get_geocode(address=address)
                    address = address.save()
                else:
                    return False

                if not BingMatrixService.build_matrices(start=address, end=list(self.__addresses)):
                    print(f'Failed to build matrix between {location} and {self.__locations}')
                print(f'Added new location {location}')
                self.__locations.add(location)
                if self.__addresses.get(address):
                    self.__addresses[address] += 1
                else:
                    self.__addresses[address] = 1
                print(f'LocationManager State {self.__locations}\n')
                return True
        return False

    def add_collection(self, locations: list):
        """Adds this list of locations to the graph database.

        If locations is None, no change occurs. Otherwise, each location in this list is added to the graph
        database.
        """
        if locations:
            for location in locations:
                self.add(location)

    def get_distance_savings(self, location1: Location, location2: Location):
        """Gets the savings (in meters) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if self.__depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if self.__depot in self.__locations and location1 in self.__locations and location2 in self.__locations:
            return self.__get_distance_saved(location1, location2)
        else:
            if self.__depot not in self.__locations:
                self.add(self.__depot)
            if location1 not in self.__locations:
                self.add(location1)
            if location2 not in self.__locations:
                self.add(location2)
        return self.__get_distance_saved(location1, location2)

    def get_duration_savings(self, location1: Location, location2: Location):
        """Gets the savings (in minutes) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if self.__depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if self.__depot in self.__locations and location1 in self.__locations and location2 in self.__locations:
            return self.__get_duration_saved(location1, location2)
        else:
            if self.__depot not in self.__locations:
                self.add(self.__depot)
            if location1 not in self.__locations:
                self.add(location1)
            if location2 not in self.__locations:
                self.add(location2)
        return self.__get_duration_saved(location1, location2)

    def __get_distance_saved(self, location1: Address, location2: Address):
        """Computes the savings distance between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        return self.__depot.distance(location1) + self.__depot.distance(location2) - location1.distance(location2)

    def __get_duration_saved(self, location1: Address, location2: Address):
        """Computes the savings duration between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        return self.__depot.duration(location1) + self.__depot.duration(location2) - location1.duration(location2)


class SavingsManager:
    def __init__(self, db_connection: str, depot: Address, locations: list):
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


class NodeParser:
    @staticmethod
    def create_drivers(drivers):
        node_drivers = []
        return node_drivers

    @staticmethod
    def create_locations(locations):
        node_locations = []
        return node_locations


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

    __NUMBER_OF_ITERATIONS = 100

    def __init__(self, db_connection: str, depot: Address, drivers: list, locations: list,
                 prioritize_volunteer: bool = False):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_locations(locations)
        self.__depot = NodeParser.create_locations(depot)[0]
        self.__location_manager = LocationManager(db_connection=db_connection, depot=self.__depot)
        self.__location_manager.add_collection(locations=locations)
        self.__savings_manager = SavingsManager(db_connection=db_connection, depot=self.__depot,
                                                locations=self.__locations)
        self.__prioritize_volunteer = prioritize_volunteer
        self.__drivers_heap = self.__build_driver_heap()
        self.__objective_function_value = sys.maxsize
        self.__best_allocation = None
        self.__objective_function_heap = []

    def __build_driver_heap(self) -> list:
        drivers_heap = []
        if self.__drivers:
            # Build a dictionary of driver's index: driver's capacity
            driver_dictionary = {index: driver.capacity for index, driver in enumerate(self.__drivers)}
            driver_dictionary = sorted(driver_dictionary.items(), key=lambda x: x[1], reverse=True)

            if self.__prioritize_volunteer:
                volunteers = []
                employees = []
                for index, driver_capacity in driver_dictionary:
                    if self.__drivers[index].is_volunteer():
                        volunteers.append(self.__drivers)
                    elif self.__drivers[index].is_fulltime():
                        employees.append(self.__drivers)
                drivers_heap.extend(volunteers)
                drivers_heap.extend(employees)
            else:
                for index, driver_capacity in driver_dictionary:
                    drivers_heap.append(self.__drivers[index])
        return drivers_heap

    def __build_routes(self):
        objective_function_value = sys.maxsize
        heapq.heapify(self.__objective_function_heap)
        best_allocation = []
        for index in range(RouteManager.__NUMBER_OF_ITERATIONS):
            print(f'\n\033[1m Iteration number \033[0m {index + 1}')
            drivers = copy.deepcopy(self.__drivers_heap)
            for driver in drivers:
                driver.reset()

            locations = copy.deepcopy(self.__locations)
            for location in locations:
                location.reset()

            savings_manager = SavingsManager(db_connection=self.__location_manager.connection,
                                             depot=self.__location_manager.depot, locations=locations)
            solver_status, drivers = self.__build_route_instance(savings_manager=savings_manager, locations=locations,
                                                                 drivers_heap=drivers)
            objective_function_distance, objective_function_duration = RouteManager.__get_instance_objective_function(
                drivers)

            if solver_status == RouteManager._State.SOLVED:
                heapq.heappush(self.__objective_function_heap, objective_function_distance)
                if objective_function_value > objective_function_distance:
                    objective_function_value = objective_function_distance
                    best_allocation = copy.deepcopy(drivers)
                    self.__locations = copy.deepcopy(locations)

        if self.__objective_function_value > objective_function_value:
            self.__objective_function_value = objective_function_value
            self.__best_allocation = copy.deepcopy(best_allocation)

    def __build_route_instance(self, savings_manager: SavingsManager, locations: list, drivers_heap: list):
        assigned_locations_set = set()
        if len(locations) == 1:
            print(f'\n\033[1m Processing single location \033[0m {locations[0]}')
            for driver in drivers_heap[::-1]:
                print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                if driver.get_departure() is None:
                    driver.set_departure(self.__location_manager.depot)
                if driver.route.__is_open and driver.add(pair=Pair(locations[0], locations[0])):
                    break
                if locations[0].is_assigned:
                    assigned_locations_set.add(locations[0])
                if len(assigned_locations_set) == len(locations):
                    break
        elif savings_manager:
            for pair in savings_manager:
                print(f'\n\033[1m Processing pair\033[0m ({pair.first}, {pair.last})')
                for driver in drivers_heap:
                    print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                    if driver.__departure() is None:
                        driver.set_departure(self.__location_manager.depot)
                    if driver.__route.__is_open and driver.add(pair=pair):
                        break
                if pair.is_assignable():
                    print(f'{RouteManager._State.INFEASIBLE}')
                if pair.first.is_assigned:
                    assigned_locations_set.add(pair.first)
                if pair.last.is_assigned:
                    assigned_locations_set.add(pair.last)
                if len(assigned_locations_set) == len(locations):
                    break

        for driver in drivers_heap:
            if len(driver.route) <= 1:
                driver.__route.departure = None
                driver.__route = None
            elif len(driver.route) > 1 and driver.route.is_open:
                driver.route.close_route()
        return RouteManager._State.SOLVED, drivers_heap

    @staticmethod
    def __get_instance_objective_function(drivers):
        objective_function_distance = 0
        objective_function_duration = 0
        for driver in drivers:
            if driver.__route:
                objective_function_distance += driver.__route.__total_distance
                objective_function_duration += driver.__route.__total_duration
        return objective_function_distance, objective_function_duration

    def request_routes(self, customers: list, drivers: list):
        response = self.__build_routes()

    def __build_response(self):
        routes = []
        for driver in self.__drivers:
            if not driver.route.is_empty():
                routes.append(driver.route.serialize())

        response = json.dumps({
            'solver_status': '',
            'message': '',
            'description': '',
            'routes': routes,
        })
        return response


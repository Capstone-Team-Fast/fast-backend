import copy
import enum
import heapq
import json
import sys

import neomodel

from routing.exceptions import RouteStateException, AddressDoesNotExist
from routing.models.location import Address, Pair, Location
from routing.services import BingGeocodeService, BingMatrixService


class DriverManager:
    def __init__(self):
        self.drivers = list()


class LocationManager:
    def __init__(self, db_connection: neomodel.db, depot: Location):
        self.depot = depot
        self.connection = db_connection
        self.locations = set()
        self.__addresses = dict()

    def remove(self, location: Location):
        if len(self.locations) == 0:
            raise StopIteration
        if not isinstance(location, Location):
            raise ValueError(f'Type {type(location)} not supported.')
        self.locations.remove(location)
        if self.__addresses.get(location.address):
            self.__addresses[location.address] -= 1
            if self.__addresses[location.address] == 0:
                del self.__addresses[location.address]

    def get_locations(self) -> list:
        return list(self.locations)

    def add(self, location: Location):
        """Add the location argument to the graph database.

        This method ensures that a location, by the time it is added to the graph database, has its coordinates set.
        The coordinates consist of a latitude and a longitude.
        """
        if location:
            if location not in self.locations:
                if location not in Location.nodes.all():
                    location.save()

                address = location.address
                if address and (address.latitude is None or address.longitude is None):
                    print(f'\nRetrieving geocode for location {address}\n')
                    address.latitude, address.longitude = BingGeocodeService.get_geocode(address=address)
                    address = address.save()
                else:
                    raise AddressDoesNotExist(f'Location {location} has no address.')

                if not BingMatrixService.build_matrices(start=address, end=list(self.__addresses)):
                    print(f'Failed to build matrix between {location} and {self.locations}')
                print(f'Added new location {location}')
                self.locations.add(location)
                if self.__addresses.get(address):
                    self.__addresses[address] += 1
                else:
                    self.__addresses[address] = 1
                print(f'LocationManager State {self.locations}\n')

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
        if self.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if self.depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_distance_saved(location1, location2)
        else:
            if self.depot not in self.locations:
                self.add(self.depot)
            if location1 not in self.locations:
                self.add(location1)
            if location2 not in self.locations:
                self.add(location2)
        return self.__get_distance_saved(location1, location2)

    def get_duration_savings(self, location1: Location, location2: Location):
        """Gets the savings (in minutes) between these two locations.

        This implementation guarantees that either location is in the graph database.
        """
        if self.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if location1 is None or location2 is None:
            return 0.0
        if self.depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_duration_saved(location1, location2)
        else:
            if self.depot not in self.locations:
                self.add(self.depot)
            if location1 not in self.locations:
                self.add(location1)
            if location2 not in self.locations:
                self.add(location2)
        return self.__get_duration_saved(location1, location2)

    def size(self):
        """Gets the number of locations being currently managed."""
        return len(self.locations)

    def __get_distance_saved(self, location1: Address, location2: Address):
        """Computes the savings distance between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        return self.depot.distance(location1) + self.depot.distance(location2) - location1.distance(location2)

    def __get_duration_saved(self, location1: Address, location2: Address):
        """Computes the savings duration between two locations.

        This helper function ensures that there is an edge between the two locations.
        """
        return self.depot.duration(location1) + self.depot.duration(location2) - location1.duration(location2)


class SavingsManager:
    def __init__(self, db_connection: str, depot: Address, locations: list):
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

    NUMBER_OF_ITERATIONS = 100

    def __init__(self, db_connection: str, depot: Address, drivers: list, locations: list,
                 prioritize_volunteer: bool = False):
        self.drivers = drivers
        self.locations = locations
        self.location_manager = LocationManager(db_connection=db_connection, depot=depot)
        self.location_manager.add_collection(locations=locations)
        self.savings_manager = SavingsManager(db_connection=db_connection, depot=depot, locations=locations)
        self.prioritize_volunteer = prioritize_volunteer
        self.drivers_heap = self.build_driver_heap()
        self.objective_function_value = sys.maxsize
        self.best_allocation = None
        self.objective_function_heap = []

    def build_driver_heap(self) -> list:
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
        objective_function_value = sys.maxsize
        heapq.heapify(self.objective_function_heap)
        best_allocation = []
        for index in range(RouteManager.NUMBER_OF_ITERATIONS):
            print(f'\n\033[1m Iteration number \033[0m {index + 1}')
            drivers = copy.deepcopy(self.drivers_heap)
            for driver in drivers:
                driver.reset()

            locations = copy.deepcopy(self.locations)
            for location in locations:
                location.reset()

            savings_manager = SavingsManager(db_connection=self.location_manager.connection,
                                             depot=self.location_manager.depot, locations=locations)
            solver_status, drivers = self.build_route_instance(savings_manager=savings_manager, locations=locations,
                                                               drivers_heap=drivers)
            objective_function_distance, objective_function_duration = RouteManager.get_instance_objective_function(
                drivers)

            if solver_status == RouteManager._State.SOLVED:
                heapq.heappush(self.objective_function_heap, objective_function_distance)
                if objective_function_value > objective_function_distance:
                    objective_function_value = objective_function_distance
                    best_allocation = copy.deepcopy(drivers)
                    self.locations = copy.deepcopy(locations)

        if self.objective_function_value > objective_function_value:
            self.objective_function_value = objective_function_value
            self.best_allocation = copy.deepcopy(best_allocation)

    def build_route_instance(self, savings_manager: SavingsManager, locations: list, drivers_heap: list):
        assigned_locations_set = set()
        if len(locations) == 1:
            print(f'\n\033[1m Processing single location \033[0m {locations[0]}')
            for driver in drivers_heap[::-1]:
                print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                if driver.get_departure() is None:
                    driver.set_departure(self.location_manager.depot)
                if driver.route.is_open and driver.add(pair=Pair(locations[0], locations[0])):
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
                    if driver.departure() is None:
                        driver.set_departure(self.location_manager.depot)
                    if driver.__route.is_open and driver.add(pair=pair):
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
            if len(driver.__route) <= 1:
                driver.__route.departure = None
                driver.__route = None
            elif len(driver.__route) > 1 and driver.__route.is_open:
                driver.__route.close_route()
        return RouteManager._State.SOLVED, drivers_heap

    @staticmethod
    def get_instance_objective_function(drivers):
        objective_function_distance = 0
        objective_function_duration = 0
        for driver in drivers:
            if driver.__route:
                objective_function_distance += driver.__route.__total_distance
                objective_function_duration += driver.__route.__total_duration
        return objective_function_distance, objective_function_duration

    def request_routes(self, customers: list, drivers: list):
        response = self.build_response()
        RouteManager.send_routes(response)

    def build_response(self):
        response = json.dumps({})
        return response

    def send_routes(self):
        pass

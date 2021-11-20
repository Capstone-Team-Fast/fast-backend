import copy
import enum
import json
import sys

import neomodel

from routing.exceptions import RouteStateException
from routing.models.language import Language
from routing.models.location import Address, Pair, Location, Customer
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
    def create_departure(departures):
        node_departures = []
        if departures:
            for location in departures:
                location = json.loads(location)
                customer = NodeParser.parse_customer(location)
                address = NodeParser.parse_address(location['location'])
                customer.set_address(address)
                for language in location['languages']:
                    language = NodeParser.parse_language(language)
                    customer.language.connect(language)
                node_departures.append(customer)
        return node_departures

    @staticmethod
    def create_customers(customers):
        node_customers = []
        if customers:
            for location in customers:
                location = json.loads(location)
                customer = NodeParser.parse_customer(location).save()

                address = NodeParser.parse_address(location['location'])
                if address not in Address.nodes.all():
                    address.save()
                else:
                    node_set = Address.nodes.filter(address=address.address, city=address.city, state=address.state,
                                                    zipcode=address.zipcode)
                    address = node_set[0]
                customer.set_address(address)

                for language in location['languages']:
                    language = NodeParser.parse_language(language)
                    if language not in Language.nodes.all():
                        language.save()
                    else:
                        node_set = Language.nodes.filter(language=language.language)
                        language = node_set[0]
                    customer.language.connect(language)

                node_customers.append(customer)
        return node_customers

    @staticmethod
    def parse_customer(customer):
        return Customer(external_id=customer['id'], demand=customer['quantity'],
                        is_center=customer['location']['is_center'])

    @staticmethod
    def parse_address(geographical_location):
        return Address(external_id=geographical_location['id'], address=geographical_location['address'],
                       city=geographical_location['city'], state=geographical_location['state'],
                       zipcode=geographical_location['zipcode'])

    @staticmethod
    def parse_language(language):
        return Language(external_id=language['id'], language=language['name'])


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

    def __init__(self, db_connection: str):
        self.__db_connection = db_connection
        self.__drivers = []
        self.__locations = []
        self.__drivers_heap = []
        self.__objective_function_value = sys.maxsize
        self.__depot = None
        self.__location_manager = None
        self.__savings_manager = None
        self.__prioritize_volunteer = False
        self.__best_allocation = None
        self.__objective_function_values_list = []

    def request_routes(self, departure, locations: list, drivers: list):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_customers(locations)
        self.__depot = NodeParser.create_customers(departure)[0]
        self.__location_manager = LocationManager(db_connection=self.__db_connection, depot=self.__depot)
        self.__location_manager.add_collection(locations=locations)
        self.__savings_manager = SavingsManager(db_connection=self.__db_connection, depot=self.__depot,
                                                locations=self.__locations)
        self.__drivers_heap = self.__build_driver_heap()
        self.__prioritize_volunteer = False
        self.__objective_function_value, self.__best_allocation, self.__objective_function_values_list = \
            self.__build_routes()
        return self.__build_response()

    def __build_response(self):
        routes = []
        for driver in self.__best_allocation:
            if not driver.route.is_empty:
                routes.append(driver.route.serialize())

        response = json.dumps({
            'solver_status': '',
            'message': '',
            'description': '',
            'routes': routes,
        })
        return response

    @property
    def objective_function_value(self):
        return self.__objective_function_value if self.__objective_function_value != sys.maxsize else None

    @property
    def best_assignment(self):
        return self.__best_allocation

    @property
    def objective_function_values(self):
        return self.__objective_function_values_list

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
        global_objective_function_value = sys.maxsize
        objective_function_values_list = []
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
            local_objective_function_distance, local_objective_function_duration = \
                RouteManager.__get_instance_objective_function(drivers)

            if solver_status == RouteManager._State.SOLVED:
                objective_function_values_list.append(local_objective_function_distance)
                if global_objective_function_value > local_objective_function_distance:
                    global_objective_function_value = local_objective_function_distance
                    best_allocation = copy.deepcopy(drivers)
        return global_objective_function_value, best_allocation, objective_function_values_list

    def __build_route_instance(self, savings_manager: SavingsManager, locations: list, drivers_heap: list):
        if len(locations) == 1:
            print(f'\n\033[1m Processing single location \033[0m {locations[0]}')
            for driver in drivers_heap[::-1]:
                print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                if driver.departure is None:
                    driver.set_departure(self.__location_manager.depot)
                if driver.route.is_open and driver.add(pair=Pair(locations[0], locations[0])):
                    break
        elif savings_manager:
            assigned_locations_list = list()
            for pair in savings_manager:
                print(f'\n\033[1m Processing pair\033[0m ({pair.first}, {pair.last})')
                for driver in drivers_heap:
                    print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                    if driver.departure is None:
                        driver.set_departure(self.__location_manager.depot)
                    if driver.route.is_open and driver.add(pair=pair):
                        break
                if pair.is_assignable():
                    print(f'{RouteManager._State.INFEASIBLE}')
                if pair.first.is_assigned:
                    assigned_locations_list.append(pair.first)
                if pair.last.is_assigned:
                    assigned_locations_list.append(pair.last)
                if len(assigned_locations_list) == len(locations):
                    break

        for driver in drivers_heap:
            if driver.route.is_empty:
                driver.route.departure = None
                driver.route = None
            elif not driver.route.is_empty and driver.route.is_open:
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

import copy
import datetime
import enum
import heapq
import json
import sys

import neomodel

from routing.exceptions import RouteStateException
from routing.models.availability import Availability
from routing.models.driver import Driver
from routing.models.language import Language
from routing.models.location import Address, Pair, Location, Customer, Depot
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
        self.add(depot)

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
                if isinstance(location, Customer):
                    if location not in Customer.nodes.all():
                        location.save()
                elif isinstance(location, Depot):
                    if location not in Depot.nodes.all():
                        location.save()

                if location.address.zipcode == 99999:
                    print('Found!')

                address = location.address
                if address and (address.latitude is None or address.longitude is None):
                    print(f'\nRetrieving geocode for location {address}\n')
                    address.latitude, address.longitude = BingGeocodeService.get_geocode(address=address)
                    address = address.save()

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
        savings = []
        if locations:
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    if locations[i].uid != locations[j].uid:
                        pair = Pair(locations[i], locations[j])
                        pair.set_origin(self.__location_manager.depot)
                        saving = self.__location_manager.get_distance_savings(location1=pair.location1,
                                                                              location2=pair.location2)
                        pair.set_saving(saving)
                        savings.append(pair)
        savings.sort(reverse=True)
        return savings

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

    class _Status(enum.Enum):
        ALL_LOCATIONS_ASSIGNED = 1
        SOME_LOCATIONS_ASSIGNED = 2
        NO_LOCATIONS_ASSIGNED = 3

    class _Alphabet(enum.Enum):
        FALSE = 0
        TRUE = 1
        DONE = 2

    __NUMBER_OF_ITERATIONS = 1

    def __init__(self, db_connection: str):
        try:
            neomodel.db.set_connection(db_connection)
        except ValueError:
            raise ValueError(f'Expecting url format: bolt://user:password@localhost:7687 but got {db_connection}')
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
        self.__final_locations = None
        self.__objective_function_values_list = []

    def request_routes(self, departure: str, locations: list, drivers: list):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_customers(locations)
        self.__depot = NodeParser.create_departure(departure)
        return RouteManager.response_template()

    def request_routes_test(self, departure: str, locations: list, drivers: list):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_customers(locations)
        self.__depot = NodeParser.create_departure(departure)
        self.__drivers_heap = self.__build_driver_heap()
        self.__prioritize_volunteer = False
        self.__objective_function_value, self.__best_allocation, self.__objective_function_values_list, \
        self.__final_locations = self.__build_routes()
        return self.__build_response()

    def __build_response(self):
        routes = []
        for driver in self.__best_allocation:
            if not driver.route.is_empty:
                routes.append(json.loads(driver.route.serialize()))

        response = json.dumps({
            'solver_status': '',
            'message': '',
            'description': '',
            'routes': routes,
        })

        print()
        for driver in self.__best_allocation:
            if not driver.route.is_empty:
                print(f'Driver {driver.uid} Status: {driver.employee_status} Delivery Limit: {driver.max_delivery}'
                      f' itinerary: {driver.route} with total demand {driver.route.total_demand}'
                      f' with capacity {driver.capacity}')
                for customer in driver.route.itinerary:
                    if not customer.is_center and customer.is_assigned:
                        print(f'\tCustomer {customer.uid} at {customer.address} with demand {customer.demand} '
                              f'is assigned')
            else:
                print(f'Driver {driver.uid} is not used. Capacity = {driver.capacity}')
            print()

        print()
        for customer in self.__final_locations:
            if customer.is_assigned:
                print(f'Customer {customer.uid} at {customer.address} with demand {customer.demand} is assigned')
            else:
                print(f'Customer {customer.uid} at {customer.address} with demand {customer.demand} is not assigned')
            print()
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
        final_locations = []
        for index in range(RouteManager.__NUMBER_OF_ITERATIONS):
            print(f'\n\033[1m Iteration number \033[0m {index + 1}')
            drivers = copy.deepcopy(self.__drivers_heap)
            for driver in drivers:
                driver.reset()

            locations = copy.deepcopy(self.__locations)
            for location in locations:
                location.reset()

            savings_manager = SavingsManager(db_connection=self.__db_connection, depot=self.__depot,
                                             locations=locations)
            solver_status, drivers = self.__build_route_instance(savings_manager=savings_manager, locations=locations,
                                                                 drivers_heap=drivers)
            local_objective_function_distance, local_objective_function_duration = \
                RouteManager.__get_instance_objective_function(drivers)

            if solver_status == RouteManager._State.SOLVED:
                objective_function_values_list.append(local_objective_function_distance)
                if global_objective_function_value > local_objective_function_distance:
                    global_objective_function_value = local_objective_function_distance
                    best_allocation = copy.deepcopy(drivers)
                    final_locations = copy.deepcopy(locations)
        return global_objective_function_value, best_allocation, objective_function_values_list, final_locations

    def __tally_locations(self, locations: list):
        tally = []
        heapq.heapify(tally)
        if locations:
            for location in locations:
                heapq.heappush(tally, location.uid)
        return tally

    def __build_route_instance(self, savings_manager: SavingsManager, locations: list, drivers_heap: list):
        if len(locations) == 1:
            print(f'\n\033[1m Processing single location \033[0m {locations[0]}')
            for driver in drivers_heap[::-1]:
                print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                if driver.departure is None:
                    driver.set_departure(self.__depot)
                if driver.route.is_open and driver.add(pair=Pair(locations[0], None)):
                    break
                if locations[0].is_assigned:
                    break
        elif savings_manager:
            locations_to_insert = self.__tally_locations(locations)
            assigned_locations_list = list()
            heapq.heapify(assigned_locations_list)
            for pair in savings_manager:
                print(f'\n\033[1m Processing pair\033[0m ({pair.first}, {pair.last})')
                for driver in drivers_heap:
                    print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m Capacity:\033[0m {driver.capacity}')
                    if driver.departure is None:
                        driver.set_departure(self.__depot)
                    if driver.route.is_open and driver.add(pair=pair):
                        break
                if pair.is_assignable():
                    print(f'{RouteManager._State.INFEASIBLE}')
                if pair.first.is_assigned:
                    if pair.first.uid not in assigned_locations_list:
                        heapq.heappush(assigned_locations_list, pair.first.uid)
                if pair.last.is_assigned:
                    if pair.last.uid not in assigned_locations_list:
                        heapq.heappush(assigned_locations_list, pair.last.uid)
                if assigned_locations_list == locations_to_insert:
                    break

        for driver in drivers_heap:
            if driver.route.is_empty:
                driver.reset()
            elif not driver.route.is_empty and driver.route.is_open:
                driver.route.close_route()
        return RouteManager._State.SOLVED, drivers_heap

    @staticmethod
    def __get_instance_objective_function(drivers):
        objective_function_distance = 0
        objective_function_duration = 0
        for driver in drivers:
            if driver.route:
                objective_function_distance += driver.route.total_distance
                objective_function_duration += driver.route.total_duration
        return objective_function_distance, objective_function_duration

    @staticmethod
    def response_template():
        return json.dumps({
            'solver_status': 1,  # Different status code based on one of 3 scenarios
            'message': '',  # Short description
            'others': [],  # Clients' id not assigned
            'description': '',
            'routes': [
                {
                    'id': 1,
                    'created_on': '2021-10-19T20:44:43.125437Z',
                    'total_quantity': 9,
                    'total_distance': 10.2,
                    'total_duration': 11.3,
                    'assigned_to': {
                        'id': 1,
                        'first_name': 'First_1',
                        'last_name': 'Last_1',
                        'capacity': 50,
                        'employee_status': 'P',
                        'availability': [
                            {'id': 1, 'day': 'Sunday'}, {'id': 2, 'day': 'Monday'}, {'id': 3, 'day': 'Tuesday'}
                        ],
                        'languages': [
                            {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'},
                            {'id': 3, 'language': 'Spanish'}
                        ],
                    },
                    'itinerary': [
                        {
                            'id': 1,
                            'is_center': True,
                            'address': {
                                'id': 1,
                                'address': 'Center',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68111,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            }
                        },
                        {
                            'id': 2,
                            'is_center': False,
                            'address': {
                                'id': 3,
                                'address': 'Customer_1',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68123,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            },
                            'demand': 9,
                            'languages': [
                                {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'},
                                {'id': 3, 'language': 'Spanish'}
                            ]
                        },
                        {
                            'id': 1,
                            'is_center': True,
                            'address': {
                                'id': 1,
                                'address': 'Center',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68111,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            }
                        },
                    ],
                },
                {
                    'id': 1,
                    'created_on': '2021-10-19T20:44:43.125437Z',
                    'total_quantity': 9,
                    'total_distance': 10.2,
                    'total_duration': 11.3,
                    'assigned_to': {
                        'id': 2,
                        'first_name': 'First_2',
                        'last_name': 'Last_2',
                        'capacity': 10,
                        'employee_status': 'P',
                        'availability': [
                            {'id': 1, 'day': 'Sunday'}, {'id': 2, 'day': 'Monday'}, {'id': 3, 'day': 'Tuesday'}
                        ],
                        'languages': [
                            {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'},
                            {'id': 3, 'language': 'Spanish'}
                        ],
                    },
                    'itinerary': [
                        {
                            'id': 1,
                            'is_center': True,
                            'address': {
                                'id': 1,
                                'address': 'Center',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68111,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            }
                        },
                        {
                            'id': 2,
                            'is_center': False,
                            'address': {
                                'id': 3,
                                'address': 'Customer_1',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68123,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            },
                            'demand': 9,
                            'languages': [
                                {'id': 1, 'language': 'English'}, {'id': 2, 'language': 'French'},
                                {'id': 3, 'language': 'Spanish'}
                            ]
                        },
                        {
                            'id': 1,
                            'is_center': True,
                            'address': {
                                'id': 1,
                                'address': 'Center',
                                'city': 'Omaha',
                                'state': 'NE',
                                'zipcode': 68111,
                                'coordinates': {'latitude': 98.23, 'longitude': -23.23}
                            }
                        },
                    ],
                }
            ],
        })


class NodeParser:
    @staticmethod
    def create_drivers(drivers: list):
        node_drivers = []
        if drivers:
            for driver in drivers:
                driver = json.loads(driver)
                driver_node = NodeParser.parse_driver(driver)
                if driver_node not in Driver.nodes.all():
                    driver_node.save()
                else:
                    node_set = Driver.nodes.filter(first_name=driver_node.first_name, last_name=driver_node.last_name,
                                                   employee_status=driver_node.employee_status)
                    object_node = node_set[0]
                    object_node.capacity = driver_node.capacity
                    object_node.start_time = driver_node.start_time
                    object_node.end_time = driver_node.end_time
                    object_node.max_delivery = driver_node.max_delivery
                    driver_node = object_node
                    driver_node.save()

                driver_node = NodeParser.set_languages(driver_node, driver['languages'])
                driver_node = NodeParser.set_availability(driver_node, driver['availability'])
                node_drivers.append(driver_node)
        return node_drivers

    @staticmethod
    def create_departure(departure: str):
        node_departure = None
        if departure:
            departure = json.loads(departure)
            node_departure = Depot()
            if node_departure not in Depot.nodes.all():
                node_departure.save()
            else:
                node_set = Depot.nodes.filter(uid=node_departure.uid, is_center=node_departure.is_center)
                node_departure = node_set[0]
                node_departure.save()
            address = NodeParser.parse_address(departure['location'])
            node_departure.set_address(address)
        return node_departure

    @staticmethod
    def create_customers(customers: list):
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
                customer = NodeParser.set_languages(customer, location['languages'])
                node_customers.append(customer)
        return node_customers

    @staticmethod
    def parse_driver(driver: dict):
        if driver.get('employee_status') and driver['employee_status'] == 'employee':
            employee_status = Driver.Role.EMPLOYEE.value
        else:
            employee_status = Driver.Role.VOLUNTEER.value

        driver_node = Driver(external_id=driver['id'], first_name=driver['first_name'], last_name=driver['last_name'],
                             capacity=driver['capacity'], employee_status=employee_status)
        if employee_status == Driver.Role.VOLUNTEER.value:
            driver_node.max_delivery = driver['delivery_limit']
        if driver.get('duration'):
            driver_node.end_time = driver_node.start_time + datetime.timedelta(hours=driver['duration'])
        else:
            driver_node.end_time = driver_node.start_time + datetime.timedelta(hours=24)
        return driver_node

    @staticmethod
    def parse_customer(customer: dict):
        return Customer(external_id=customer['id'], demand=customer['quantity'],
                        is_center=customer['location']['is_center'])

    @staticmethod
    def parse_address(geographical_location: dict):
        return Address(external_id=geographical_location['id'], address=geographical_location['address'],
                       city=geographical_location['city'], state=geographical_location['state'],
                       zipcode=geographical_location['zipcode'])

    @staticmethod
    def parse_language(language: dict):
        if language.get('name'):
            if language.get('name') in Language.options():
                return Language(external_id=language['id'], language=language['name'])
            else:
                Language.add_languages(language.get('name'))
                return Language(external_id=language['id'], language=language['name'])

    @staticmethod
    def set_languages(node, languages: dict):
        if languages:
            for language in languages:
                language = NodeParser.parse_language(language)
                if language not in Language.nodes.all():
                    language.save()
                else:
                    node_set = Language.nodes.filter(language=language.language)
                    language = node_set[0]
                node.language.connect(language)
        return node

    @staticmethod
    def set_availability(driver: Driver, availabilities: dict):
        if availabilities:
            for key in availabilities.keys():
                if key != 'id':
                    if availabilities[key]:
                        availability = Availability(day=key.capitalize())
                        if availability not in Availability.nodes.all():
                            availability.save()
                        else:
                            node_set = Availability.nodes.filter(day=availability.day)
                            availability = node_set[0]
                        driver.is_available_on.connect(availability)
        return driver

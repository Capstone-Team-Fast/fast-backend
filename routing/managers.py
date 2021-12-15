import copy
import datetime
import enum
import json
import sys
from typing import Set

import neomodel
from neomodel import UniqueIdProperty

from routing.exceptions import RouteStateException, GeocodeError
from routing.models.availability import Availability
from routing.models.driver import Driver
from routing.models.language import Language
from routing.models.location import Address, Pair, Location, Customer, Depot
from routing.services import BingGeocodeService, BingMatrixService


class LocationManager:
    """This class provides the mechanism for manipulating Location nodes used as part of the routing algorithm.

        This implementation supports locations with the same address. That is, there needs not be a one-one relationship
        between locations and addresses for the operations defines in this class to work as expected.
    """
    def __init__(self, db_connection: neomodel.db, depot: Location):
        """Creates a LocationManager.

            @param db_connection: A string representing the connection string to a neo4j graph database.
            @param depot: The departure location for the locations managed by this manager.
        """
        self.__depot = depot
        self.__connection = db_connection
        self.__locations = set()
        self.__addresses = dict()
        self.add(depot)

    @property
    def depot(self):
        """A property to retrieve the departure point for the locations managed by this manager.

            @return the departure point for the locations managed by this manager.
        """
        return self.__depot

    @property
    def connection(self):
        """A property to retrieve the connection string of the neo4j graph database used by this manager.

            @return the connection string of the neo4j graph database used by this manager.
        """
        return self.__connection

    @property
    def locations(self) -> list:
        """A property to retrieve the list of locations managed by this manager.

            @return the list of locations managed by this manager.
        """
        return list(self.__locations)

    @property
    def size(self):
        """A property to retrieve the number of locations being currently managed.

            @return the number of locations being currently managed.
        """
        return len(self.__locations)

    def remove(self, location: Location):
        """Provides the mechanism to remove a location from the underlining data structure.

            @param location: The location to remove from the list of locations being managed.
        """
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
        """Adds the location argument to the graph database.

            This method ensures that a location, by the time it is added to the graph database, has its coordinates set.
            The coordinates consist of a latitude and a longitude.

            @param location: A location to add to the graph database. This location must be of type
            'routing.models.location.Location'.
        """
        if location:
            if location not in self.__locations:
                if isinstance(location, Customer):
                    if location not in Customer.nodes.all():
                        location.save()
                elif isinstance(location, Depot):
                    if location not in Depot.nodes.all():
                        location.save()

                address = location.address
                if address and (address.latitude is None or address.longitude is None):
                    print(f'\nRetrieving geocode for location {address}\n')
                    try:
                        address.latitude, address.longitude = BingGeocodeService.get_geocode(address=address)
                        address = address.save()
                    except GeocodeError as err:
                        raise err

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

            @param locations: A list of locations to add to the graph database. Each of these locations must be of type
            'routing.models.location.Location'.
        """
        if locations:
            for location in locations:
                self.add(location)

    def get_distance_savings(self, location1: Location, location2: Location):
        """Provides the mechanism to compute the savings (in miles) between these two locations.

            This implementation guarantees that either location is in the graph database and that they are connected.

            The savings distance is computing as follows:
                    S = d_{*i} + d_{*j} - d_{ij}, where * representing the location of departure.

            @param location1: Address of the starting location. This location representing the starting point.
            @param location2: Address of the destination. This location representing the arrival point.
            @return the savings distance between the two locations.
            @raise RouteStateException when the departure location is not set prior to calling this method.
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
        """Provides the mechanism to compute the savings (in minutes) between these two locations.

            This implementation guarantees that either location is in the graph database and that they are connected.

            The savings duration is computing as follows:
                    S = d_{*i} + d_{*j} - d_{ij}, where * representing the location of departure.

            @param location1: Address of the starting location. This location representing the starting point.
            @param location2: Address of the destination. This location representing the arrival point.
            @return the savings duration between the two locations.
            @raise RouteStateException when the departure location is not set prior to calling this method.
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

            This helper function ensures that there is an edge between the two locations. The savings distance is
            computing as follows:
                S = d_{*i} + d_{*j} - d_{ij}, where * representing the location of departure.

            @param location1: Address of the starting location. This location representing the starting point.
            @param location2: Address of the destination. This location representing the arrival point.
            @return the savings duration between the two locations.
        """
        return self.__depot.distance(location1) + self.__depot.distance(location2) - location1.distance(location2)

    def __get_duration_saved(self, location1: Address, location2: Address):
        """Computes the savings duration between two locations.

            This helper function ensures that there is an edge between the two locations. The savings duration is
            computing as follows:
                S = d_{*i} + d_{*j} - d_{ij}, where * representing the location of departure.

            @param location1: Address of the starting location. This location representing the starting point.
            @param location2: Address of the destination. This location representing the arrival point.
            @return the savings duration between the two locations.
        """
        return self.__depot.duration(location1) + self.__depot.duration(location2) - location1.duration(location2)


class SavingsManager:
    """This class provides the mechanism for computing the savings distance between any pair of locations used by the
    routing algorithm.

        This class implements the __next__ method as well as __iter__.
    """
    def __init__(self, db_connection: str, depot: Address, locations: list):
        """Creates a new SavingsManager.

            @param db_connection: A string representing the connection string to a neo4j graph database.
            @param depot: The departure location for the locations managed by this manager.
            @param locations: A list of locations to used in the computation of the savings distance. Each of these
            locations must be of type 'routing.models.location.Location'.
        """
        self.__location_manager = LocationManager(db_connection=db_connection, depot=depot)
        self.__heap, self.__valid_locations, self.__invalid_locations = self.__heapify(locations=locations)

    @property
    def invalid_locations(self):
        """A property to retrieve the list of invalid locations.

            A location is invalid is its address cannot be geocoded.

            @return the list of invalid locations.
        """
        return list(self.__invalid_locations)

    @property
    def valid_locations(self):
        """A property to retrieve the list of valid locations.

            A location is valid is its address can be geocoded.

            @return the list of invalid locations.
        """
        return list(self.__valid_locations)

    def __heapify(self, locations: list):
        savings = []
        invalid_locations = set()
        valid_locations = set()
        if locations:
            for i in range(len(locations)):
                for j in range(i + 1, len(locations)):
                    if locations[i].uid != locations[j].uid:
                        pair = Pair(locations[i], locations[j])
                        pair.set_origin(self.__location_manager.depot)
                        try:
                            saving = self.__location_manager.get_distance_savings(location1=pair.first,
                                                                                  location2=pair.last)
                            pair.set_saving(saving)
                            savings.append(pair)
                            valid_locations.add(pair.first)
                            valid_locations.add(pair.last)
                        except GeocodeError:
                            if pair.first.address.longitude is None or pair.first.address.latitude is None:
                                invalid_locations.add(pair.first)
                            else:
                                valid_locations.add(pair.first)
                            if pair.last.address.longitude is None or pair.last.address.latitude is None:
                                invalid_locations.add(pair.last)
                            else:
                                valid_locations.add(pair.last)
                            continue
        savings.sort(reverse=True)
        return savings, valid_locations, invalid_locations

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
        TERMINATED = 3
        INFEASIBLE = 4

    class _Status(enum.Enum):
        ALL_LOCATIONS_ASSIGNED = 1
        SOME_LOCATIONS_ASSIGNED = 2
        NO_LOCATIONS_ASSIGNED = 3
        OTHER_ERROR = 4
        NO_LOCATIONS_TO_ASSIGN = 5

    class _Alphabet(enum.Enum):
        FALSE = 0
        TRUE = 1
        DONE = 2

    __NUMBER_OF_ITERATIONS = 1
    __Response = {
        'solver_status': '',  # Different status code based on one of 3 scenarios
        'message': '',  # Short description
        'description': '',  # Detailed description
        'others': [],  # Clients' id not assigned
        'routes': [],  # List of routes assigned to driver
    }

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
        self.__prioritize_volunteer = False
        self.__best_allocation = None
        self.__final_locations = None
        self.__objective_function_values_list = []
        self.__invalid_locations = set()

    def request_routes(self, departure: str, locations: list, drivers: list):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_customers(locations)
        self.__depot = NodeParser.create_departure(departure)
        return RouteManager.response_template()

    def request_routes_test(self, departure: str, locations: list, drivers: list):
        self.__drivers = NodeParser.create_drivers(drivers)
        self.__locations = NodeParser.create_customers(locations)
        self.__depot = NodeParser.create_departure(departure)
        self.__prioritize_volunteer = self.__contains_volunteers()
        self.__drivers_heap = self.__build_driver_heap()
        self.__objective_function_value, self.__best_allocation, self.__objective_function_values_list, \
            self.__final_locations = self.__build_routes()
        return self.__build_response()

    def __contains_volunteers(self):
        for driver in self.__drivers:
            if driver.employee_status == Driver.Role.VOLUNTEER.value:
                return True
        return False

    def __build_response(self):
        routes = []
        for driver in self.__best_allocation:
            if not driver.route.is_empty:
                routes.append(json.loads(driver.route.serialize()))

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

        RouteManager.__Response['routes'] = routes
        return json.dumps(RouteManager.__Response)

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
                        volunteers.append(self.__drivers[index])
                    elif self.__drivers[index].is_full_time():
                        employees.append(self.__drivers[index])
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
            solver_status, drivers, locations = self.__build_route_instance(savings_manager=savings_manager,
                                                                            locations=locations,
                                                                            drivers_heap=drivers)
            local_objective_function_distance, local_objective_function_duration = \
                RouteManager.__get_instance_objective_function(drivers)

            if solver_status == RouteManager._State.TERMINATED:
                objective_function_values_list.append(local_objective_function_distance)
                if global_objective_function_value > local_objective_function_distance:
                    global_objective_function_value = local_objective_function_distance
                    best_allocation = copy.deepcopy(drivers)
                    final_locations = copy.deepcopy(locations)
        return global_objective_function_value, best_allocation, objective_function_values_list, final_locations

    @staticmethod
    def __tally_locations(locations: list) -> Set[UniqueIdProperty]:
        tally = set()
        if locations:
            for location in locations:
                tally.add(location.uid)
        return tally

    def __build_route_instance(self, savings_manager: SavingsManager, locations: list, drivers_heap: list):
        assigned_locations_list: Set[UniqueIdProperty] = set()
        locations_to_insert: Set[UniqueIdProperty] = set()
        if len(locations) == 1:
            locations_to_insert = RouteManager.__tally_locations(locations)
            try:
                print(f'\n\033[1m Processing single location \033[0m {locations[0]}')
                for driver in drivers_heap[::-1]:
                    print(f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m UID:\033[0m {driver.uid} \033[1m '
                          f'Status:\033[0m {driver.employee_status} '
                          f'\033[1m Capacity:\033[0m {driver.capacity}')
                    if driver.departure is None:
                        driver.set_departure(self.__depot)
                    if driver.route.is_open and driver.add(pair=Pair(locations[0], None)):
                        break
                    if locations[0].is_assigned:
                        assigned_locations_list.add(locations[0].uid)
                        break
            except GeocodeError:
                if locations[0].address.latitude is None or locations[0].address.longitude is None:
                    self.__invalid_locations.add(locations[0])
        elif savings_manager:
            self.__invalid_locations.update(savings_manager.invalid_locations)
            numbers_of_drivers = 0
            max_drivers_count = len(drivers_heap)
            state = RouteManager._State.HARD_SOLVING
            while state != RouteManager._State.TERMINATED:
                if numbers_of_drivers == max_drivers_count:
                    break
                numbers_of_drivers = min(numbers_of_drivers + 1, max_drivers_count)
                print(f'\n==========Using minimum of {numbers_of_drivers} drivers==========\n')
                drivers = drivers_heap[:numbers_of_drivers]
                for driver in drivers:
                    driver.reset()
                local_savings_manager = copy.deepcopy(savings_manager)
                locations = local_savings_manager.valid_locations
                locations.extend(local_savings_manager.invalid_locations)
                locations_to_insert = self.__tally_locations(locations)
                self.__invalid_locations.update(savings_manager.invalid_locations)
                assigned_locations_list = set()
                for pair in local_savings_manager:
                    try:
                        print(f'\n\033[1mProcessing pair\033[0m ({pair.first}, {pair.last})')
                        for driver in drivers:
                            print(
                                f'\tUsing \033[1m driver\033[0m \'{driver}\' \033[1m UID:\033[0m {driver.uid} \033[1m '
                                f'Capacity:\033[0m {driver.capacity}')
                            if driver.departure is None:
                                driver.set_departure(self.__depot)
                            if driver.route.is_open and driver.add(pair=pair):
                                break
                        if pair.is_assignable():
                            print(f'{RouteManager._State.INFEASIBLE}')
                        if pair.first.is_assigned:
                            assigned_locations_list.add(pair.first.uid)
                        if pair.last.is_assigned:
                            assigned_locations_list.add(pair.last.uid)
                        if assigned_locations_list == locations_to_insert:
                            break
                    except GeocodeError:
                        if pair.first.address.latitude is None or pair.last.address.longitude is None:
                            self.__invalid_locations.add(pair.first)
                        if pair.first.address.latitude is None or pair.last.address.longitude is None:
                            self.__invalid_locations.add(pair.last)
                        continue
                if assigned_locations_list == locations_to_insert:
                    state = RouteManager._State.TERMINATED
                else:
                    state = RouteManager._State.INFEASIBLE

        for driver in drivers_heap:
            if driver.route.is_empty:
                driver.reset()
            elif not driver.route.is_empty and driver.route.is_open:
                driver.route.close_route()

        if len(assigned_locations_list) == 0 and assigned_locations_list == locations_to_insert:
            RouteManager.__Response['solver_status'] = RouteManager._Status.NO_LOCATIONS_TO_ASSIGN.value
            RouteManager.__Response['message'] = RouteManager._Status.NO_LOCATIONS_TO_ASSIGN.name
            RouteManager.__Response['description'] = 'No location to assign.'
        elif len(assigned_locations_list) != 0 and assigned_locations_list == locations_to_insert:
            RouteManager.__Response['solver_status'] = RouteManager._Status.ALL_LOCATIONS_ASSIGNED.value
            RouteManager.__Response['message'] = RouteManager._Status.ALL_LOCATIONS_ASSIGNED.name
            RouteManager.__Response['description'] = 'All locations were assigned.'
        elif len(locations_to_insert) == 0 or len(self.__invalid_locations) == len(locations_to_insert):
            RouteManager.__Response['solver_status'] = RouteManager._Status.NO_LOCATIONS_ASSIGNED.value
            RouteManager.__Response['message'] = RouteManager._Status.NO_LOCATIONS_ASSIGNED.name
            RouteManager.__Response['description'] = 'No address could be geocoded.'
        elif len(self.__invalid_locations) == 0 and assigned_locations_list != locations_to_insert:
            RouteManager.__Response['solver_status'] = RouteManager._Status.OTHER_ERROR.value
            RouteManager.__Response['message'] = RouteManager._Status.OTHER_ERROR.name
            if len(assigned_locations_list) == 0:
                RouteManager.__Response['description'] = 'Assignment is infeasible.'
            else:
                RouteManager.__Response['description'] = 'Some addresses were assigned.'

            for uid in list(locations_to_insert.difference(assigned_locations_list)):
                location = Customer.nodes.get_or_none(uid=uid)
                if location:
                    self.__invalid_locations.add(location)
        else:
            RouteManager.__Response['solver_status'] = RouteManager._Status.SOME_LOCATIONS_ASSIGNED.value
            RouteManager.__Response['message'] = RouteManager._Status.SOME_LOCATIONS_ASSIGNED.name
            RouteManager.__Response['description'] = 'Some addresses could not be geocoded.'

        RouteManager.__Response['others'] = [address.external_id for address in self.__invalid_locations]

        return RouteManager._State.TERMINATED, drivers_heap, locations

    @staticmethod
    def __get_instance_objective_function(drivers):
        objective_function_distance = 0
        objective_function_duration = 0
        for driver in drivers:
            if driver.route:
                objective_function_distance += driver.route.total_distance
                objective_function_duration += driver.route.total_duration
        return objective_function_distance, objective_function_duration


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
                                                   external_id=driver_node.external_id,
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
            node_departure = NodeParser.parse_depot(depot=departure)
            if node_departure in Depot.nodes.all():
                node_set = Depot.nodes.filter(external_id=node_departure.external_id,
                                              is_center=node_departure.is_center)
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
                customer = NodeParser.parse_customer(location)
                if customer in Customer.nodes.all():
                    node_set = Customer.nodes.filter(external_id=customer.external_id)
                    customer = node_set[0]
                customer.save()
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
        if driver.get('employee_status') and driver['employee_status'].lower() == 'employee':
            employee_status = Driver.Role.EMPLOYEE.value
        else:
            employee_status = Driver.Role.VOLUNTEER.value

        driver_node = Driver(external_id=driver['id'], first_name=driver['first_name'], last_name=driver['last_name'],
                             capacity=driver['capacity'], employee_status=employee_status)
        if employee_status == Driver.Role.VOLUNTEER.value:
            driver_node.max_delivery = driver['delivery_limit']
        if driver.get('duration'):
            driver_node.end_time = driver_node.start_time + datetime.timedelta(hours=int(driver['duration']))
        else:
            driver_node.end_time = driver_node.start_time + datetime.timedelta(hours=24)
        return driver_node

    @staticmethod
    def parse_customer(customer: dict):
        return Customer(external_id=customer['id'], demand=customer['quantity'])

    @staticmethod
    def parse_depot(depot: dict):
        return Depot(external_id=depot['location']['id'])

    @staticmethod
    def parse_address(geographical_location: dict):
        return Address(external_id=geographical_location['id'], address=geographical_location['address'],
                       city=geographical_location['city'], state=geographical_location['state'],
                       zipcode=geographical_location['zipcode'])

    @staticmethod
    def parse_language(language: dict):
        if language.get('name'):
            if language.get('name') in Language.options():
                return Language(external_id=language['id'], language=language.get('name'))
            else:
                name = ' '.join([part.capitalize() for part in language.get('name').split()])
                return Language(external_id=language['id'], language=name)

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

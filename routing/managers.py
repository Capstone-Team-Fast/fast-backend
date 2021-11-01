import enum
from heapq import heappush, heapify, heappop

import neomodel

from routing.exceptions import RelationshipError, RouteStateException
from routing.models.location import Location, Pair
from routing.services import BingGeocodeService


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
        LocationManager.connection = db_connection

    @staticmethod
    def remove(location: Location):
        if len(LocationManager.locations) == 0:
            raise StopIteration
        if not isinstance(location, Location):
            raise ValueError
        LocationManager.locations.remove(location)

    @staticmethod
    def get_locations() -> list:
        return list(LocationManager.locations)

    @staticmethod
    def add(location: Location):
        if not isinstance(location, Location):
            raise ValueError
        if location not in LocationManager.locations:
            if location.latitude is None or location.longitude is None:
                location.latitude, location.longitude = BingGeocodeService.get_geocode(location=location)
                location = location.save()

            # BingMatrixService.build_matrices(start=location, end=list(LocationManager.locations))
            LocationManager.locations.add(location)

    @staticmethod
    def add_collection(locations: list):
        if not locations:
            raise ValueError

        for location in locations:
            if len(LocationManager.locations) == 0:
                LocationManager.add(location)
            else:
                if location not in LocationManager.locations:
                    LocationManager.add(location)

    @staticmethod
    def get_distance(location1: Location, location2: Location):
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
        if LocationManager.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
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
        if LocationManager.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
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
        return len(LocationManager.locations)

    @staticmethod
    def __get_distance_saved(location1: Location, location2: Location):
        LocationManager.__all_links_exist(location1, location2)

        return (LocationManager.depot.neighbor.relationship(location1).distance
                + LocationManager.depot.neighbor.relationship(location2).distance
                - location1.neighbor.relationship(location2).distance)

    @staticmethod
    def __get_duration_saved(location1: Location, location2: Location):
        LocationManager.__all_links_exist(location1, location2)

        return (LocationManager.depot.neighbor.relationship(location1).duration
                + LocationManager.depot.neighbor.relationship(location2).duration
                - location1.neighbor.relationship(location2).duration)

    @staticmethod
    def __all_links_exist(location1: Location, location2: Location):
        if LocationManager.depot is None:
            raise RouteStateException('This route has no departure. Set the departure before proceeding.')
        if LocationManager.depot.neighbor.relationship(location1) is None:
            raise RelationshipError(
                'There is no link between node \'{}\' and node \'{}\''.format(LocationManager.depot, location1))
        if LocationManager.depot.neighbor.relationship(location2) is None:
            raise RelationshipError(
                'There is no link between node \'{}\' and node \'{}\''.format(LocationManager.depot, location2))
        if location1.neighbor.relationship(location2) is None:
            raise RelationshipError('There is no link between node \'{}\' and node \'{}\''.format(location1, location2))


class SavingsManager:
    def __init__(self, db_connection: str, depot: Location, locations: list):
        self.depot = depot
        self.__location_manager = LocationManager(db_connection=db_connection, depot=depot)
        self.__heap = self.__heapify(locations=locations)

    def __heapify(self, locations: list):
        heap = []
        heapify(heap)
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                if locations[i] != locations[j]:
                    pair = Pair(locations[i], locations[j])
                    savings = self.__location_manager.get_distance_savings(location1=pair.location1,
                                                                           location2=pair.location2)
                    heappush(heap, (-1 * savings, pair))
        return heap

    def __next__(self):
        if len(self.__heap) > 0:
            savings, pair = heappop(self.__heap)
            return -1 * savings, pair
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
        self.savings_manager = SavingsManager(db_connection=db_connection, depot=depot, locations=locations)
        self.drivers_heap = []
        self.prioritize_volunteer = prioritize_volunteer

    def insert(self, pair: Pair) -> _State:
        for driver in self.drivers:
            inserted, cumulative_duration, cumulative_distance, cumulative_quantity = driver.route.add(pair=pair)
            if cumulative_duration > driver.end_time - driver.start_time:
                driver.route.undo()
                driver.route.close_route()
            elif cumulative_quantity > driver.capacity:
                driver.route.undo()
                driver.route.close_route()
            if not inserted:
                continue
            else:
                return RouteManager._State.HARD_SOLVING

        # After insertion update drivers_heap so that retrieving driver with shortest distance is constant
        return self._State.INFEASIBLE

    def build_routes(self):
        for savings, pair in self.savings_manager:
            for driver in self.drivers:
                print(f"Processing pair ({pair.first()}, {pair.last()})")
                if driver.get_departure() is None:
                    driver.set_departure(self.location_manager.depot)
                if driver.add(pair=pair):
                    continue

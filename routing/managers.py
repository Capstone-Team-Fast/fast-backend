import enum
from heapq import heappush, heapify, heappop

import neomodel

from routing.models.location import Location, Pair
from routing.services import BingGeocodeService, BingMatrixService


class DriverManager:
    def __init__(self):
        self.drivers = list()


class LocationManager:

    def __init__(self, db_connection: neomodel.db, depot: Location):
        self.depot = depot
        self.locations = set()
        self.connection = db_connection

    def remove(self, location: Location):
        if len(self.locations) == 0:
            raise StopIteration
        if not isinstance(location, Location):
            raise ValueError
        self.locations.remove(location)

    def get_locations(self) -> list:
        return list(self.locations)

    def add(self, location: Location):
        if not isinstance(location, Location):
            raise ValueError
        if location not in self.locations:
            if location.latitude is None or location.longitude is None:
                location.latitude, location.longitude = BingGeocodeService.get_geocode(location=location)
                location = location.save()

            BingMatrixService.build_matrices(start=location, end=list(self.locations))
            self.locations.add(location)

    def add_collection(self, locations: list):
        if not locations:
            raise ValueError

        for location in locations:
            if len(self.locations) == 0:
                self.add(location)
            else:
                if location not in self.locations:
                    self.add(location)

    def set_depot(self, depot: Location):
        self.depot = depot

    def get_distance(self, location1: Location, location2: Location):
        if location1 == location2:
            return 0.0

        if location1 in self.locations and location2 in self.locations:
            return location1.neighbor.relationship(location2).distance

        if location1 not in self.locations:
            self.add(location1)

        if location2 not in self.locations:
            self.add(location2)

        return location1.neighbor.relationship(location2).distance

    def get_duration(self, location1: Location, location2: Location):
        if location1 == location2:
            return 0.0

        if location1 in self.locations and location2 in self.locations:
            return location1.neighbor.relationship(location2).duration

        if location1 not in self.locations:
            self.add(location1)

        if location2 not in self.locations:
            self.add(location2)
        return location1.neighbor.relationship(location2).duration

    def get_distance_savings(self, location1: Location, location2: Location):
        if self.depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_distance_saved(location1, location2)
        if self.depot not in self.locations:
            self.add(self.depot)
        if location1 not in self.locations:
            self.add(location1)
        if location2 not in self.locations:
            self.add(location2)
        return self.__get_distance_saved(location1, location2)

    def get_duration_savings(self, location1: Location, location2: Location):
        if self.depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_duration_saved(location1, location2)
        if self.depot not in self.locations:
            self.add(self.depot)
        if location1 not in self.locations:
            self.add(location1)
        if location2 not in self.locations:
            self.add(location2)
        return self.__get_duration_saved(location1, location2)

    def get_properties(self):
        pass

    def size(self):
        return len(self.locations)

    def __get_distance_saved(self, location1: Location, location2: Location):
        return (self.depot.neighbor.relationship(location1).distance
                + self.depot.neighbor.relationship(location2).distance
                - location1.neighbor.relationship(location2).distance)

    def __get_duration_saved(self, location1: Location, location2: Location):
        return (self.depot.neighbor.relationship(location1).duration
                + self.depot.neighbor.relationship(location2).duration
                - location1.neighbor.relationship(location2).duration)


class SavingsManager:
    def __init__(self, db_connection: str, depot: Location, locations: list):
        self.depot = depot
        self.heap = self.__heapify(locations=locations)
        self.locationManager = LocationManager(db_connection=db_connection, depot=depot)

    def __heapify(self, locations: list):
        heap = []
        heapify(heap)
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                if locations[i] != locations[j]:
                    pair = Pair(locations[i], locations[j])
                    savings = self.locationManager.get_distance_savings(location1=pair.location1,
                                                                        location2=pair.location2)
                    heappush(heap, (-1 * savings, pair))
        return heap

    def __next__(self):
        if len(self.heap) >= 0:
            savings, pair = heappop(self.heap)
            return -1 * savings, pair
        raise StopIteration


class RouteManager:
    """
    Uses constraints to build routes and assign them to drivers
    """

    class State(enum.Enum):
        IDLE = 0
        HARD_SOLVING = 1
        SOFT_SOLVING = 2
        SOLVED = 3
        INFEASIBLE = 4

    class Alphabet(enum.Enum):
        FALSE = 0
        TRUE = 1
        DONE = 2

    def __init__(self, db_connection: str, depot: Location, drivers: list, locations: list,
                 prioritize_volunteer: bool = False):
        self.drivers = drivers
        self.locations = locations
        self.locationManager = LocationManager(db_connection=db_connection, depot=depot)
        self.savingsManager = SavingsManager(db_connection=db_connection, depot=depot, locations=locations)
        self.drivers_heap = []
        self.prioritize_volunteer = prioritize_volunteer

    def insert(self, pair: Pair) -> State:
        if len(self.locations) == 1:
            for location in pair.get_pair():
                self.add(location)
        elif pair.get_first() and pair.get_second():
            location1, location2 = pair.get_pair()
            if ((location1 in self.locations) ^ (location2 in self.locations)) and pair.is_assignable():
                if location1 in self.locations and not location1.is_interior(self) and not location2.is_assigned:
                    self.add(location2)
                elif location2 in self.locations and not location2.is_interior(self) and not location1.is_assigned:
                    self.add(location1)

        # After insertion update drivers_heap so that retrieving driver with shortest distance is constant

    def build_routes(self):
        pass

    def add(self, location):
        pass

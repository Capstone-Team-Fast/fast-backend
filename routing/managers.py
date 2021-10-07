import neomodel

from routing import services
from routing.models.location import Location


class DriverManager:
    def __init__(self):
        self.drivers = list()



class LocationManager:

    def __init__(self, db_connection: neomodel.db):
        self.locations = set()
        self.connection = db_connection
        self.distanceMatrixService = services.DistanceMatrixService()
        self.durationMatrixService = services.DurationMatrixService()
        self.__set_locations()

    def delete(self, location: Location):
        if not isinstance(location, Location):
            return NotImplemented
        self.locations.remove(location)

    def get_locations(self):
        return self.locations

    def add(self, location: Location):
        if not isinstance(location, Location):
            return NotImplemented
        if location not in self.locations:
            self.distanceMatrixService.build_distance_matrix(list(self.locations), location)
            self.durationMatrixService.build_duration_matrix(list(self.locations), location)
            self.locations.add(location)

    def add_collection(self, locations: list):
        if not locations:
            return TypeError

        for location in locations:
            if len(self.locations) == 0:
                self.add(location)
            else:
                if location not in self.locations:
                    self.add(location)

    def is_fully_connected(self):
        pass

    def get_distance(self, location1: Location, location2: Location):
        if location1 in self.locations and location2 in self.locations:
            return location1.neighbor.relationship(location2).distance

        if location1 not in self.locations:
            self.add(location1)

        if location2 not in self.locations:
            self.add(location2)

        return location1.neighbor.relationship(location2).distance

    def get_duration(self, location1: Location, location2: Location):
        if location1 in self.locations and location2 in self.locations:
            return location1.neighbor.relationship(location2).duration

        if location1 not in self.locations:
            self.add(location1)

        if location2 not in self.locations:
            self.add(location2)
        return location1.neighbor.relationship(location2).duration

    def get_distance_savings(self, depot: Location, location1: Location, location2: Location):
        if depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_distance_saved(depot, location1, location2)
        if depot not in self.locations:
            self.add(depot)
        if location1 not in self.locations:
            self.add(location1)
        if location2 not in self.locations:
            self.add(location2)
        return self.__get_distance_saved(depot, location1, location2)

    def get_duration_savings(self, depot: Location, location1: Location, location2: Location):
        if depot in self.locations and location1 in self.locations and location2 in self.locations:
            return self.__get_duration_saved(depot, location1, location2)
        if depot not in self.locations:
            self.add(depot)
        if location1 not in self.locations:
            self.add(location1)
        if location2 not in self.locations:
            self.add(location2)
        return self.__get_duration_saved(depot, location1, location2)

    def get_properties(self):
        pass

    def size(self):
        return len(self.locations)

    def __get_distance_saved(self, depot: Location, location1: Location, location2: Location):
        return (depot.neighbor.relationship(location1).distance
                + depot.neighbor.relationship(location2).distance
                - location1.neighbor.relationship(location2).distance)

    def __get_duration_saved(self, depot: Location, location1: Location, location2: Location):
        return (depot.neighbor.relationship(location1).duration
                + depot.neighbor.relationship(location2).duration
                - location1.neighbor.relationship(location2).duration)

    def __set_locations(self):
        for location in Location.nodes.all():
            self.add(location)
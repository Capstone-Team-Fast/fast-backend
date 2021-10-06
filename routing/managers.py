import neomodel

from routing import services
from routing.models.location import Location


class DriverManager:
    pass


class LocationManager:

    def __init__(self, db_connection: neomodel.db):
        self.locations = set()
        self.connection = db_connection
        self.__set_locations()

    def __set_locations(self):
        for location in Location.nodes.all():
            self.add(location)

    def delete(self, location: Location):
        if not isinstance(location, Location):
            return NotImplemented
        self.locations.remove(location)

    def get_locations(self):
        return self.locations

    def add(self, location: Location):
        if not isinstance(location, Location):
            return NotImplemented
        self.locations.add(location)

    def add_collection(self, locations):
        if not locations:
            return TypeError

        for location in locations:
            if len(self.locations) == 0:
                self.add(location)
            else:
                if not (location in self.locations):
                    services.DistanceMatrixService.get_distance_matrix(list(self.locations), location)
                    self.add(location)

    def is_fully_connected(self):
        pass

    def get_distance(self, location1, location2):
        pass

    def get_duration(self, location1, location2):
        pass

    def get_properties(self):
        pass

    def size(self):
        return len(self.locations)

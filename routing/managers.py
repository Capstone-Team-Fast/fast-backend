import neomodel

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


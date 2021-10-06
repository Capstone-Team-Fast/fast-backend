# https://docs.mapbox.com/api/search/geocoding/
from routing.models.location import Location


class GeocodeService:
    pass


class DistanceMatrixService:

    def __init__(self, url=''):
        self.url = url

    def build_distance_matrix(self, locations: list, location: Location):
        # list is empty
        # list is not empty
        pass


class DurationMatrixService:

    def __init__(self, url=''):
        self.url = url

    def build_duration_matrix(self, locations: list, location: Location):
        pass

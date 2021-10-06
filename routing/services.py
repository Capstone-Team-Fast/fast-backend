# https://docs.mapbox.com/api/search/geocoding/
from routing import models


class GeocodeService:
    pass


class DistanceMatrixService:
    @staticmethod
    def get_distance_matrix(location1: models.Location, location2: models.Location):
        pass

    @staticmethod
    def get_distance_matrix(locations: list, location: models.Location):
        pass


class DurationMatrixService:
    @staticmethod
    def get_duration_matrix(location1: models.Location, location2: models.Location):
        pass

    @staticmethod
    def get_duration_matrix(locations: list, location: models.Location):
        pass

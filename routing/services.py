# https://docs.mapbox.com/api/search/geocoding/
import os
from urllib.parse import quote

from routing.exceptions import GeocodeError
from routing.models.location import Location
import requests


class GeocodeService:
    __DEFAULT_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    __API_KEY = os.environ.get('BING_MAPS_API_KEY', os.environ['BING_MAPS_API_KEY'])

    def __init__(self, base_url: str = ''):
        self.__base_url = GeocodeService.__DEFAULT_URL if base_url == '' else base_url

    def get_geocode(self, location: Location, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        response = self.__request_geocode(location=location, payload=payload, headers=headers)
        return self.__extract_coordinates(response)

    def __request_geocode(self, location: Location, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        encoded_location = quote(string=str(location), safe='')
        url = "{BASE_URL}?query={QUERY_STRING}&key={API_KEY}".format(BASE_URL=self.__base_url,
                                                                     QUERY_STRING=encoded_location,
                                                                     API_KEY=self.__API_KEY)
        payload = payload
        headers = headers
        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    def __extract_coordinates(self, response: dict):
        if 'resourceSets' in response.keys():
            resource_sets = response['resourceSets'][0] if len(response['resourceSets']) > 0 else None
            if resource_sets and 'resources' in resource_sets:
                resources = resource_sets['resources'][0] if len(resource_sets['resources']) > 0 else None
                if resources and 'point' in resources.keys():
                    point = resources['point'] if len(resources['point']) > 0 else None
                    if point and 'coordinates' in point.keys():
                        coordinates = point['coordinates']
                        if coordinates[0] < -90 or coordinates[0] > 90:
                            raise GeocodeError('Latitude must be between -90 and 90')
                        if coordinates[1] < -180 or coordinates[1] > 180:
                            raise GeocodeError('Longitude must be between -180 and 180')
                        return coordinates[0], coordinates[1]
        raise GeocodeError('API Error')


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

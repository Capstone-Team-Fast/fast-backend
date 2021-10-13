# https://docs.mapbox.com/api/search/geocoding/
import os
from urllib.parse import quote

from routing.exceptions import GeocodeError
from routing.models.location import Location
import requests


class GeocodeService:
    __DEFAULT_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    __API_KEY = os.environ.get('BING_MAPS_API_KEY', os.environ['BING_MAPS_API_KEY'])

    @staticmethod
    def get_geocode(location: Location, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        response = GeocodeService.__request_geocode(location=location, payload=payload, headers=headers)
        return GeocodeService.__get_coordinates(response)

    @staticmethod
    def __request_geocode(location: Location, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        encoded_location = quote(string=str(location), safe='')
        url = "{BASE_URL}?query={QUERY_STRING}&key={API_KEY}".format(BASE_URL=GeocodeService.__DEFAULT_URL,
                                                                     QUERY_STRING=encoded_location,
                                                                     API_KEY=GeocodeService.__API_KEY)
        payload = payload
        headers = headers
        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    @staticmethod
    def __get_coordinates(response: dict):
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


class MatrixService:
    """
    This class defines the logic for retrieving distance and duration matrices of a list of locations.
    """
    __DEFAULT_URL = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix'
    __API_KEY = os.environ.get('BING_MAPS_API_KEY', os.environ['BING_MAPS_API_KEY'])
    __duration_matrix = []
    __distance_matrix = []

    @staticmethod
    def __request_matrices(start: Location, end: list, travel_mode: str = 'driving', chunk_size: int = 25):
        if start.latitude is None or start.longitude is None:
            start.latitude, start.longitude = GeocodeService.get_geocode(start)
            start = start.save()

        origins = [{'latitude': start.latitude, 'longitude': start.longitude}]

        for index in range(0, len(end), chunk_size):
            if index + chunk_size < len(end):
                chunks = end[index:index + chunk_size]
            else:
                chunks = end[index:]

            destinations = [{'latitude': location.latitude, 'longitude': location.longitude} for location in chunks]

            url = '{BASE_URL}?key={API_KEY}'.format(BASE_URL=MatrixService.__DEFAULT_URL,
                                                    API_KEY=MatrixService.__API_KEY)
            data = {
                'origins': origins,
                'destinations': destinations,
                'travelMode': travel_mode,
            }
            headers = {
                'Content-Length': 450,
                'Content-Type': 'application/json'
            }
            requests.get(url=url, data=data, headers=headers)

    @staticmethod
    def build_duration_matrix(start: Location, end: list):
        pass

    @staticmethod
    def build_distance_matrix(start: Location, end: list):
        pass

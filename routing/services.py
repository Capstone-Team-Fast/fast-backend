import json
import os
from abc import ABC
from urllib.parse import quote

import requests

from routing.exceptions import GeocodeError, MatrixServiceError
from routing.models.location import Address


class GeocodeService(ABC):

    @staticmethod
    def get_geocode(location: Address, payload=None, headers=None):
        pass


class BingGeocodeService(GeocodeService):
    __DEFAULT_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    __API_KEY = os.environ.get('BING_MAPS_API_KEY', os.environ['BING_MAPS_API_KEY'])

    @staticmethod
    def get_geocode(address: Address, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        response = BingGeocodeService.__request_geocode(location=address, payload=payload, headers=headers)
        return BingGeocodeService.__get_coordinates(response)

    @staticmethod
    def __request_geocode(location: Address, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        encoded_location = quote(string=str(location), safe='')
        url = "{BASE_URL}?query={QUERY_STRING}&key={API_KEY}".format(BASE_URL=BingGeocodeService.__DEFAULT_URL,
                                                                     QUERY_STRING=encoded_location,
                                                                     API_KEY=BingGeocodeService.__API_KEY)
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


class MatrixService(ABC):

    @staticmethod
    def build_duration_matrix(start: Address, end: list):
        pass

    @staticmethod
    def build_distance_matrix(start: Address, end: list):
        pass


class BingMatrixService(MatrixService):
    """
    This class defines the logic for retrieving distance and duration matrices of a list of locations.
    """
    __DEFAULT_URL = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix'
    __API_KEY = os.environ.get('BING_MAPS_API_KEY', os.environ['BING_MAPS_API_KEY'])
    __duration_matrix = []
    __distance_matrix = []

    @staticmethod
    def build_matrices(start: Address, end: list, travel_mode: str = 'driving', chunk_size: int = 25) -> bool:
        if start is None or end is None:
            return False

        if start.latitude is None or start.longitude is None:
            start.latitude, start.longitude = BingGeocodeService.get_geocode(start)
            start = start.save()

        url = '{BASE_URL}?key={API_KEY}'.format(BASE_URL=BingMatrixService.__DEFAULT_URL,
                                                API_KEY=BingMatrixService.__API_KEY)

        origins = [{'latitude': start.latitude, 'longitude': start.longitude}]

        print(f'\nRequesting matrix between \'{start}\' and \'{end}\'\n')
        for index in range(0, len(end), chunk_size):
            if index + chunk_size < len(end):
                chunks = end[index:index + chunk_size]
            else:
                chunks = end[index:]

            destinations = []
            for address in chunks:
                if address:
                    if address.latitude is None or address.longitude is None:
                        print(f'\nRetrieving geocode for address {address}\n')
                        address.latitude, address.longitude = BingGeocodeService.get_geocode(address)
                        address.save()
                    if address != start and start.neighbor.relationship(address) is None:
                        destinations.append({'latitude': address.latitude, 'longitude': address.longitude})

            print(f'Destinations: {destinations}\n')

            if len(destinations) > 0:
                data = json.dumps({
                    'origins': origins,
                    'destinations': destinations,
                    'travelMode': travel_mode,
                })
                headers = {
                    'Content-Length': '450',
                    'Content-Type': 'application/json'
                }
                print(f'HTTP Data: {data}\n')

                response = requests.request("POST", url=url, data=data, headers=headers)

                if response.status_code != 200:
                    raise MatrixServiceError('API Error - HTTP Error')

                try:
                    origins, destinations, results = BingMatrixService.__get_matrices(response=response.json())
                    print(f'\nRetrieve the following matrix {results}\n')
                    BingMatrixService.__insert_matrices(origins=origins, destinations=destinations, results=results)
                except MatrixServiceError:
                    raise MatrixServiceError('API Error - Could not build matrices from HTTP request')
        return True

    @staticmethod
    def __get_matrices(response: dict):
        if response is None:
            return None

        if 'resourceSets' in response.keys():
            resource_sets = response['resourceSets'][0] if len(response['resourceSets']) > 0 else None
            if resource_sets and 'resources' in resource_sets:
                resources = resource_sets['resources'][0] if len(resource_sets['resources']) > 0 else None
                if resources:
                    if 'destinations' in resources.keys():
                        destinations = resources['destinations']
                    else:
                        raise MatrixServiceError('Key \'destinations\' not found.')
                    if 'origins' in resources.keys():
                        origins = resources['origins']
                    else:
                        raise MatrixServiceError('Key \'origins\' not found.')
                    if 'results' in resources.keys():
                        results = resources['results']
                    else:
                        raise MatrixServiceError('Key \'results\' not found.')

                    return origins, destinations, results
        raise MatrixServiceError('API Error - BING Matrix')

    @staticmethod
    def __insert_matrices(origins: list, destinations: list, results: list):
        if origins and destinations and results:
            for result in results:
                if 'destinationIndex' not in result:
                    raise MatrixServiceError('API Error - BING Matrix - Invalid key \'destinationIndex\'')
                else:
                    destination_index = result['destinationIndex']

                if 'originIndex' not in result:
                    raise MatrixServiceError('API Error - BING Matrix - Invalid key \'originIndex\'')
                else:
                    origin_index = result['originIndex']

                destination: dict = destinations[destination_index]
                origin: dict = origins[origin_index]
                location1 = Address.nodes.get(latitude=origin['latitude'], longitude=origin['longitude'])
                location2 = Address.nodes.get(latitude=destination['latitude'], longitude=destination['longitude'])
                location1.neighbor.connect(location2, {'distance': result['travelDistance'],
                                                       'duration': result['travelDuration']})
                print(f'\nConnected {location1} and {location2}\n')

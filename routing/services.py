import json
import logging
from abc import ABC
from urllib.parse import quote

import requests

from backend import settings
from routing.exceptions import GeocodeError, MatrixServiceError
from routing.models.location import Address


class GeocodeService(ABC):

    @staticmethod
    def get_geocode(location: Address, payload=None, headers=None):
        pass


class BingGeocodeService(GeocodeService):
    __DEFAULT_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    __API_KEY = settings.BING_MAPS_API_KEY

    @staticmethod
    def get_geocode(address: Address, payload=None, headers=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        response = BingGeocodeService.__request_geocode(location=address, payload=payload, headers=headers)

        # print(response)

        return BingGeocodeService.__get_coordinates(response, address)

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
    def __get_coordinates(response: dict, address: Address):
        if 'resourceSets' in response.keys():
            resource_sets = response['resourceSets'][0] if len(response['resourceSets']) > 0 else None
            if resource_sets and 'resources' in resource_sets:
                resources = resource_sets['resources'][0] if len(resource_sets['resources']) > 0 else None
                confidence = resources['confidence']
                logging.info(f'Retrieving confidence for address: {confidence}')
                if confidence == 'High':
                    if resources and resources.get('address'):
                        address_response = resources.get('address')
                        if BingGeocodeService.__validate_geocode(address_response, address):
                            if resources and 'point' in resources.keys():
                                point = resources['point'] if len(resources['point']) > 0 else None
                                if point and 'coordinates' in point.keys():
                                    coordinates = point['coordinates']
                                    if coordinates[0] < -90 or coordinates[0] > 90:
                                        logging.error('Latitude must be between -90 and 90')
                                        raise GeocodeError('Latitude must be between -90 and 90')
                                    if coordinates[1] < -180 or coordinates[1] > 180:
                                        logging.error('Longitude must be between -180 and 180')
                                        raise GeocodeError('Longitude must be between -180 and 180')
                                    return coordinates[0], coordinates[1]
                        logging.error('Invalid Geocode')
                        raise GeocodeError('Invalid Geocode')
                raise GeocodeError('Confidence Must Be High')
        logging.error('API Error')
        raise GeocodeError('API Error')

    @staticmethod
    def __validate_geocode(address_response: dict, address: Address):
        condition1 = (
                address_response.get('locality') is not None 
                and address_response.get('postalCode') is not None
                and address_response.get('countryRegion') is not None
        )
        condition2 = (
                address_response.get('countryRegion').lower() == 'United States'.lower()
        )

        return condition1 and condition2


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
    __API_KEY = settings.BING_MAPS_API_KEY
    __duration_matrix = []
    __distance_matrix = []

    @staticmethod
    def build_matrices(start: Address, end: list, travel_mode: str = 'driving', chunk_size: int = 25) -> bool:
        if start is None or end is None:
            return False

        if start in Address.nodes.all():
            node_set = Address.nodes.filter(address=start.address, city=start.city, state=start.state,
                                            zipcode=start.zipcode)
            start = node_set[0]

        if start.latitude is None or start.longitude is None:
            try:
                start.latitude, start.longitude = BingGeocodeService.get_geocode(start)
                start = start.save()
            except GeocodeError as err:
                logging.error(f"Geocode Error: {err}")
                raise err

        url = '{BASE_URL}?key={API_KEY}&distanceUnit={DISTANCE_UNIT}'.format(BASE_URL=BingMatrixService.__DEFAULT_URL,
                                                                             API_KEY=BingMatrixService.__API_KEY,
                                                                             DISTANCE_UNIT='mi')

        origins = [{'latitude': start.latitude, 'longitude': start.longitude}]

        logging.info(f'Requesting matrix between \'{start}\' and \'{end}\'')
        for index in range(0, len(end), chunk_size):
            if index + chunk_size < len(end):
                chunks = end[index:index + chunk_size]
            else:
                chunks = end[index:]

            destinations = []
            for address in chunks:
                if address:
                    if address in Address.nodes.all():
                        node_set = Address.nodes.filter(address=address.address, city=address.city, state=address.state,
                                                        zipcode=address.zipcode)
                        address = node_set[0]

                    if address.latitude is None or address.longitude is None:
                        logging.info(f'Retrieving geocode for address {address}')
                        try:
                            address.latitude, address.longitude = BingGeocodeService.get_geocode(address)
                            address.save()
                        except GeocodeError as err:
                            logging.error(f"Geocode Error: {err}")
                            raise err
                    if address != start and start.neighbor.relationship(address) is None:
                        destinations.append({'latitude': address.latitude, 'longitude': address.longitude})

            logging.info(f'Destinations: {destinations}')

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
                logging.info(f'HTTP Data: {data}')

                response = requests.request("POST", url=url, data=data, headers=headers)

                if response.status_code != 200:
                    logging.error('API Error - HTTP Error')
                    raise MatrixServiceError('API Error - HTTP Error')

                try:
                    origins, destinations, results = BingMatrixService.__get_matrices(response=response.json())
                    logging.info(f'Retrieve the following matrix {results}')
                    BingMatrixService.__insert_matrices(origins=origins, destinations=destinations, results=results)
                except MatrixServiceError:
                    logging.error('API Error - Could not build matrices from HTTP request')
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
                        logging.error('Key \'destinations\' not found.')
                        raise MatrixServiceError('Key \'destinations\' not found.')
                    if 'origins' in resources.keys():
                        origins = resources['origins']
                    else:
                        logging.error('Key \'origins\' not found.')
                        raise MatrixServiceError('Key \'origins\' not found.')
                    if 'results' in resources.keys():
                        results = resources['results']
                    else:
                        logging.error('Key \'results\' not found.')
                        raise MatrixServiceError('Key \'results\' not found.')

                    return origins, destinations, results
        logging.error('API Error - BING Matrix')
        raise MatrixServiceError('API Error - BING Matrix')

    @staticmethod
    def __insert_matrices(origins: list, destinations: list, results: list):
        if origins and destinations and results:
            for result in results:
                if 'destinationIndex' not in result:
                    logging.error('API Error - BING Matrix - Invalid key \'destinationIndex\'')
                    raise MatrixServiceError('API Error - BING Matrix - Invalid key \'destinationIndex\'')
                else:
                    destination_index = result['destinationIndex']

                if 'originIndex' not in result:
                    logging.error('API Error - BING Matrix - Invalid key \'originIndex\'')
                    raise MatrixServiceError('API Error - BING Matrix - Invalid key \'originIndex\'')
                else:
                    origin_index = result['originIndex']

                destination: dict = destinations[destination_index]
                origin: dict = origins[origin_index]
                location1 = None
                location2 = None

                node_set = Address.nodes.filter(latitude=origin['latitude'], longitude=origin['longitude'])
                if node_set:
                    location1 = node_set[0]

                node_set = Address.nodes.filter(latitude=destination['latitude'], longitude=destination['longitude'])
                if node_set:
                    location2 = node_set[0]

                if location1 and location2:
                    location1.neighbor.connect(location2, {'distance': result['travelDistance'],
                                                           'duration': result['travelDuration']})
                    logging.info(f'Connected {location1} and {location2}')

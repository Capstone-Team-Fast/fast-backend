import json
from abc import ABC
from urllib.parse import quote

import requests

from backend import settings
from routing.exceptions import GeocodeError, MatrixServiceError
from routing.models.location import Address


class GeocodeService(ABC):
    """This abstract class provides the template to be extended by any Geocoding Service.

        This class provides one method, GET_GEOCODE, which provides the signature for geocoding a node of type ADDRESS.
    """
    @staticmethod
    def get_geocode(location: Address, payload=None, headers=None):
        """This static method provides the template for geocoding a node of type ADDRESS.

        @param location: Address is to be geocoded. Address must be of type routing.models.location.Address
        @param payload: Http connection payload. Default is None
        @param headers: Http connection header. Default is None
        """
        pass


class BingGeocodeService(GeocodeService):
    """This class extends GeocodeService and provides the mechanism to geocode a physical address using the Bing
    Geocoding Service.

        This class encapsulates the Bing Geocoding Service endpoint as well as a developer key. The developer key is
        defined in the settings file under the backend app.

        Typical usage example:

        coordinates = BingGeocodeService.get_geocode(address=Address(...))
        latitude, longitude = BingGeocodeService.get_geocode(address=Address(...))
    """
    __DEFAULT_URL = 'http://dev.virtualearth.net/REST/v1/Locations'
    __API_KEY = settings.BING_MAPS_API_KEY

    @staticmethod
    def get_geocode(address: Address, payload=None, headers=None):
        """Provides the mechanism for geocoding a physical address.

        @param address: Address is to be geocoded. Address must be of type 'routing.models.location.Address'
        @param payload: Http connection payload. Default is None
        @param headers: Http connection header. Default is None
        @raise GeocodeError when an exception occurs due to geocoding. The geocoding exception can be caused by a
        variety of reasons. i- A change is the API response structure. ii- Invalid value for latitude or longitude.
        Latitude values are expected to be between [-90, 90], and longitude values are expected to be between
        [-180, 180]. When in doubt about the reason for raising this exception, consult the exception message.
        """
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        response = BingGeocodeService.__request_geocode(location=address, payload=payload, headers=headers)
        try:
            coordinates = BingGeocodeService.__get_coordinates(response, address)
        except GeocodeError as err:
            raise err
        return coordinates

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
                if resources and resources.get('address'):
                    address_response = resources.get('address')
                    if BingGeocodeService.__validate_geocode(address_response, address):
                        if resources and 'point' in resources.keys():
                            point = resources['point'] if len(resources['point']) > 0 else None
                            if point and 'coordinates' in point.keys():
                                coordinates = point['coordinates']
                                if coordinates[0] < -90 or coordinates[0] > 90:
                                    raise GeocodeError('Latitude must be between -90 and 90')
                                if coordinates[1] < -180 or coordinates[1] > 180:
                                    raise GeocodeError('Longitude must be between -180 and 180')
                                return coordinates[0], coordinates[1]
                    raise GeocodeError('Invalid Geocode')
        raise GeocodeError('API Error')

    @staticmethod
    def __validate_geocode(address_response: dict, address: Address):
        """Provides mechanism for checking the accuracy of the geocode of this address.

        A geocode is valid if the LOCALITY, POSTAL_CODE, COUNTRY_REGION returned by the Bing Geocode API match the
        address's.

        @param address_response: A dictionary representing the response returned by the Bing Geocode API.
        @param address: Address to be geocoded. This address must be of type 'routing.models.location.Address'
        """
        condition1 = (
                address_response.get('locality') is not None and address_response.get('postalCode') is not None
                and address_response.get('countryRegion') is not None
        )
        condition2 = (
                address_response.get('locality').lower() == address.city.lower()
                and int(address_response.get('postalCode')) == address.zipcode
                and address_response.get('countryRegion').lower() == address.country.lower()
        )

        return condition1 and condition2


class MatrixService(ABC):
    """This abstract provides the template to be extended by any Distance/Duration Matrix Service."""

    @staticmethod
    def build_duration_matrix(start: Address, end: list):
        """Provides the template for requesting a duration matrix between an address and a list of addresses.

        @param start: The starting address. This address must be of type 'routing.models.location.Address'
        @param end: A list of destination addresses. Each of these addresses must be of type
        'routing.models.location.Address'
        """
        pass

    @staticmethod
    def build_distance_matrix(start: Address, end: list):
        """Provides the template for requesting a distance matrix between an address and a list of addresses.

        @param start: The starting address. This address must be of type 'routing.models.location.Address'.
        @param end: A list of destination addresses. Each of these addresses must be of type
        'routing.models.location.Address'.
        """
        pass


class BingMatrixService(MatrixService):
    """This class extends MatrixService and provides the mechanism for retrieving distance and duration matrices between
    a list of locations.

        This class encapsulates the Bing Matrix Service endpoint as well as a developer key. The developer key is
        defined in the settings file under the backend app.

        Typical usage example:

        coordinates = BingGeocodeService.get_geocode(address=Address(...))
        latitude, longitude = BingGeocodeService.get_geocode(address=Address(...))
    """
    __DEFAULT_URL = 'https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix'
    __API_KEY = settings.BING_MAPS_API_KEY
    __duration_matrix = []
    __distance_matrix = []

    @staticmethod
    def build_matrices(start: Address, end: list, travel_mode: str = 'driving', chunk_size: int = 25) -> bool:
        """Provides the mechanism for getting the distance and duration matrices between an address and a list of
        addresses. It uses a POST request as described by the Bing Matrix documentation.

            Distance and duration between pairs of addresses are stored as properties in the underlining neo4j graph
            database. By default, distances are in miles and duration in minutes. Therefore, the underlining nodes
            distance and duration properties are altered.

            @param start: The starting address. This address must be of type 'routing.models.location.Address'.
            @param end: A list of destination addresses. Each of these addresses must be of type
            'routing.models.location.Address'.
            @param travel_mode: A string representing the transportation mode used. The default option is 'driving'. For
            up-to-date option consult Bing Matrix Service official documentation.
            @param chunk_size: A integer representing the maximum number of destination addresses to map to at a time.
            @return true if the distance and duration between the starting address and all the destination addresses are
            set. Otherwise, false.
            @raise GeocodeError when an exception occurs due to geocoding. The geocoding exception can be caused by a
            variety of reasons. i- A change is the API response structure. ii- Invalid value for latitude or longitude.
            Latitude values are expected to be between [-90, 90], and longitude values are expected to be between
            [-180, 180]. When in doubt about the reason for raising this exception, consult the exception message.
            @raise MatrixServiceError when an exception during retrieval of the matrices. This exception can be caused
            either at the API level, i.e., when any HTTP status code other than 200 is returned or when the structure
            of the Bing Matrix Service changes.
        """
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
                raise err

        url = '{BASE_URL}?key={API_KEY}&distanceUnit={DISTANCE_UNIT}'.format(BASE_URL=BingMatrixService.__DEFAULT_URL,
                                                                             API_KEY=BingMatrixService.__API_KEY,
                                                                             DISTANCE_UNIT='mi')

        origins = [{'latitude': start.latitude, 'longitude': start.longitude}]

        print(f'\nRequesting matrix between \'{start}\' and \'{end}\'')
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
                        print(f'\nRetrieving geocode for address {address}\n')
                        try:
                            address.latitude, address.longitude = BingGeocodeService.get_geocode(address)
                            address.save()
                        except GeocodeError as err:
                            raise err
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
                    print(f'\nConnected {location1} and {location2}\n')

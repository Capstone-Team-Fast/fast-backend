from neomodel import DoesNotExist


class GeocodeError(Exception):
    pass


class MatrixServiceError(Exception):
    pass


class RelationshipError(Exception):
    pass


class EmptyRouteException(Exception):
    pass


class RouteStateException(Exception):
    pass


class LocationStateException(Exception):
    pass

from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, DateTimeProperty, \
    UniqueIdProperty, RelationshipTo
from neomodel.contrib.spatial_properties import PointProperty


class Location(StructuredNode):
    uid = UniqueIdProperty()
    address = StringProperty(index=True, required=True)
    city = StringProperty(index=True, required=True)
    state = StringProperty(index=True, required=True)
    zipcode = IntegerProperty(index=True, required=True)
    is_center = BooleanProperty(index=True, default=False)
    coordinates = PointProperty(unique_index=True, crs='wgs-84')
    created_on = DateTimeProperty()
    modified_on = DateTimeProperty()

    distance = RelationshipTo('Location', 'DISTANCE_FROM')
    duration = RelationshipTo('Location', 'DURATION_FROM')
    savings = RelationshipTo('Location', 'SAVINGS_BETWEEN')

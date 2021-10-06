from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, DateTimeProperty, \
    UniqueIdProperty, RelationshipTo, Relationship, StructuredRel


# from neomodel.contrib.spatial_properties import PointProperty


class Weight(StructuredRel):
    distance = FloatProperty(required=True)
    duration = FloatProperty(required=True)
    savings = FloatProperty()


class Location(StructuredNode):
    uid = UniqueIdProperty()
    address = StringProperty(index=True, required=True)
    city = StringProperty(index=True, required=True)
    state = StringProperty(index=True, required=True)
    zipcode = IntegerProperty(index=True, required=True)
    is_center = BooleanProperty(index=True, default=False)
    # coordinates = PointProperty(unique_index=True, crs='wgs-84')
    latitude = FloatProperty(index=True)
    longitude = FloatProperty(index=True)
    created_on = DateTimeProperty()
    modified_on = DateTimeProperty()

    neighbor = Relationship(cls_name='Location', rel_type='CONNECTED_TO', model=Weight)

    def __hash__(self):
        return hash((self.address, self.city, self.state, self.zipcode))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.address == other.address and self.city == other.city
                and self.state == other.state and self.zipcode == other.zipcode)

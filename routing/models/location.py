from neomodel import StructuredNode, StringProperty, IntegerProperty, BooleanProperty, FloatProperty, \
    DateTimeProperty, UniqueIdProperty, Relationship, StructuredRel


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
    demand = IntegerProperty(index=True)
    latitude = FloatProperty(index=True)
    longitude = FloatProperty(index=True)
    created_on = DateTimeProperty(index=True)
    modified_on = DateTimeProperty(index=True)

    neighbor = Relationship(cls_name='Location', rel_type='CONNECTED_TO', model=Weight)

    def __init__(self, *args, **kwargs):
        super(Location, self).__init__(*args, **kwargs)
        self.is_assigned = False

    def __hash__(self):
        return hash((self.address, self.city, self.state, self.zipcode))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.address == other.address and self.city == other.city
                and self.state == other.state and self.zipcode == other.zipcode)

    def __str__(self):
        return '{address}, {city}, {state} {zipcode}'.format(address=self.address, city=self.city, state=self.state,
                                                             zipcode=self.zipcode)


class Pair:
    def __init__(self, location1: Location, location2: Location):
        if not (isinstance(location1, Location) and isinstance(location2, Location)):
            raise ValueError
        self.location1 = location1
        self.location2 = location2

    def get_first(self):
        return self.location1

    def get_second(self):
        return self.location2

    def get_pair(self):
        return self.location1, self.location2

    def is_assignable(self):
        return not (self.location1.is_assigned or self.location2.is_assigned)

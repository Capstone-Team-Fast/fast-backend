from datetime import datetime

from neomodel import StructuredNode, RelationshipTo, FloatProperty, DateTimeProperty


class Route(StructuredNode):
    total_quantity = FloatProperty(index=True)
    total_distance = FloatProperty(index=True)
    total_duration = FloatProperty(index=True)
    created_on = DateTimeProperty(default=datetime.now)

    assigned_to = RelationshipTo('routing.models.driver.Driver', 'ASSIGNED_TO')

    def __init__(self, *args, **kwargs):
        super(Route, self).__init__(args, kwargs)
        self.locations = list()

    def get_total_distance(self):
        pass

    def set_total_distance(self):
        pass

    def get_total_duration(self):
        pass

    def set_total_duration(self):
        pass

    def get_driver(self):
        pass

    def get_total_demand(self):
        pass

    def get_created_on(self):
        return self.created_on

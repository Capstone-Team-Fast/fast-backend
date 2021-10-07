from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo

from route import Route


class Driver(StructuredNode):
    ROLES = {'P': 'Employee', 'V': 'Volunteer'}

    uid = UniqueIdProperty()
    first_name = StringProperty(index=True, required=True)
    last_name = StringProperty(index=True, required=True)
    employee_status = StringProperty(index=True, choices=ROLES, required=True)
    phone = StringProperty(index=True)
    capacity = IntegerProperty(default=0)
    created_on = DateTimeProperty(default=datetime.now)
    modified_on = DateTimeProperty(default_now=True)

    serves = RelationshipTo('routing.models.location.Location', 'SERVES')
    is_available_on = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')
    speaks = RelationshipTo('routing.models.language.Language', 'SPEAKS')

    def __init__(self):
        super(Driver, self).__init__()
        self.route = Route()

    def __hash__(self):
        return hash((self.first_name, self.last_name, self.employee_status))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return (self.first_name == other.first_name and self.last_name == other.last_name
                and self.employee_status == other.employee_status)

from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo


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

    locations = RelationshipTo('routing.models.location.Location', 'SERVES')
    available = RelationshipTo('routing.models.availability.Availability', 'AVAILABLE_ON')
    languages = RelationshipTo('routing.models.language.Language', 'SPEAKS')


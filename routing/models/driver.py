from datetime import datetime

from neomodel import StructuredNode, IntegerProperty, StringProperty, DateTimeProperty, UniqueIdProperty, RelationshipTo


class Driver(StructuredNode):

    ROLES = {'P': 'Employee', 'V': 'Volunteer'}

    uid = UniqueIdProperty()
    first_name = StringProperty(index=True, required=True)
    last_name = StringProperty(index=True, required=True)
    capacity = IntegerProperty(default=0)
    employee_status = StringProperty(index=True, choices=ROLES, required=True)
    phone = StringProperty(index=True, required=True)
    created_on = DateTimeProperty(default=datetime.now)
    modified_on = DateTimeProperty(default_now=True)

    locations = RelationshipTo('routing.models.location.Location', 'SERVES')
    # availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
    # languages = models.ManyToManyField(to=Language)


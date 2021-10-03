from neomodel import StructuredNode, StringProperty, ArrayProperty


class Availability(StructuredNode):
    DAYS = {'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
            'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'}
    day = StringProperty(required=True, unique_index=True, choices=DAYS)

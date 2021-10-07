from neomodel import StructuredNode, StringProperty, ArrayProperty


class Availability(StructuredNode):
    DAYS = {'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday',
            'Thursday': 'Thursday', 'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'}
    day = StringProperty(required=True, unique_index=True, choices=DAYS)

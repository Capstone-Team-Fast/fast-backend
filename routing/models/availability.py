from neomodel import StructuredNode, StringProperty


class Availability(StructuredNode):
    """Define the 'day' property of an Availability node.

    This node represents the availability as specified by a week day. Seven different values are possible.
    These are Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday.

        Typical usage example:

        foo = Availability.create({'day': 'Monday'})
    """

    DAYS = {'Monday': 'Monday', 'Tuesday': 'Tuesday', 'Wednesday': 'Wednesday',
            'Thursday': 'Thursday', 'Friday': 'Friday', 'Saturday': 'Saturday', 'Sunday': 'Sunday'}
    day = StringProperty(required=True, unique_index=True, choices=DAYS)

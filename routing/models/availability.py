import json
import os
import sys

from neomodel import StructuredNode, StringProperty, IntegerProperty

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing import constant


class Availability(StructuredNode):
    """This class defines an Availability node.

    This node represents the availability as specified by a week day. Seven different values are possible.
    These are Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday. These values are ranked such that
    Monday has the value 1 while Sunday has the value 7.

        Typical usage example:

        foo = Availability(day='Monday')
    """

    __DAYS = {constant.MONDAY_STR: constant.MONDAY_INT, constant.TUESDAY_STR: constant.TUESDAY_INT,
              constant.WEDNESDAY_STR: constant.WEDNESDAY_INT, constant.THURSDAY_STR: constant.THURSDAY_INT,
              constant.FRIDAY_STR: constant.FRIDAY_INT, constant.SATURDAY_STR: constant.SATURDAY_INT,
              constant.SUNDAY_STR: constant.SUNDAY_INT}

    """A string representing the day of the week. Each day is unique."""
    day = StringProperty(required=True, unique_index=True, choices=__DAYS)

    """An integer representing the id of this day. Each day is assigned a unique id."""
    external_id = IntegerProperty(required=False, unique_index=True)

    @staticmethod
    def options() -> list:
        """A utility function that returns the possible values of Availability.

        These options are days of the week.
        """
        return list(Availability.__DAYS.keys())

    def __eq__(self, other):
        """Provides the mechanism for comparing two objects of type AVAILABILITY.

        Two availabilities are equal they have the same ranking. Monday is ranked with 1 and Sunday is ranked with 7.

        @param: other object to compare to.
        @return: True if the rank of this object is equal to the rank of the other.
        @raise: TypeError if the objects being compared are not AVAILABILITY objects.
        """
        if isinstance(other, type(self)):
            return Availability.__DAYS[str(other)] == Availability.__DAYS[str(self)]
        raise TypeError(f'{type(other)} not supported.')

    def __lt__(self, other):
        """Provides the mechanism for comparing two objects of type AVAILABILITY.

        An AVAILABILITY is less that another if its ranking is less than that of the other. Monday is ranked with 1 and
        Sunday is ranked with 7.

        @param: other object to compare to.
        @return: True if the rank of this object is less than the rank of the other.
        @raise: TypeError if the objects being compared are not AVAILABILITY objects.
        """
        if isinstance(other, type(self)):
            return Availability.__DAYS[str(other)] < Availability.__DAYS[str(self)]
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        """Returns a readable format for this availability.

        Availability is a day of the week. The returned value is capitalized, i.e., the first character is uppercase,
        while all other characters are lowercase.

        @return: a String representing a readable format for this availability.
        """
        return '{}'.format(str(self.day).capitalize())

    def serialize(self):
        """Serializes this availability.

        The serializer uses the JavaScript Object Notation, JSON, and serializes this availability.

            Format:
                {
                    'id': [INTEGER],
                    'day': [STRING]
                }

        @return: A JSON object representing this AVAILABILITY.
        """
        obj = json.dumps({
            'id': self.external_id,
            'day': str(self.day)
        })
        return obj

    @classmethod
    def category(cls):
        pass

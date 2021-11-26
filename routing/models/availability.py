import json
import os
import sys

from neomodel import StructuredNode, StringProperty, IntegerProperty

if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from routing import constant


class Availability(StructuredNode):
    """Define the 'day' property of an Availability node.

    This node represents the availability as specified by a week day. Seven different values are possible.
    These are Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, and Sunday.

        Typical usage example:

        foo = Availability.create({'day': 'Monday'})
    """

    __DAYS = {constant.MONDAY_STR: constant.MONDAY_INT, constant.TUESDAY_STR: constant.TUESDAY_INT,
              constant.WEDNESDAY_STR: constant.WEDNESDAY_INT, constant.THURSDAY_STR: constant.THURSDAY_INT,
              constant.FRIDAY_STR: constant.FRIDAY_INT, constant.SATURDAY_STR: constant.SATURDAY_INT,
              constant.SUNDAY_STR: constant.SUNDAY_INT}
    day = StringProperty(required=True, unique_index=True, choices=__DAYS)
    external_id = IntegerProperty(required=False, unique_index=True)

    @staticmethod
    def options() -> list:
        return list(Availability.__DAYS.keys())

    @classmethod
    def category(cls):
        pass

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return Availability.__DAYS[str(other)] == Availability.__DAYS[str(self)]
        raise TypeError(f'{type(other)} not supported.')

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return Availability.__DAYS[str(other)] < Availability.__DAYS[str(self)]
        raise TypeError(f'{type(other)} not supported.')

    def __str__(self):
        return '{}'.format(str(self.day).capitalize())

    def serialize(self):
        obj = json.dumps({
            'id': self.external_id,
            'day': str(self.day)
        })
        return obj

from neomodel import config, db

from backend import settings
from routing.models.availability import Availability
from routing.models.driver import Driver
from routing.models.location import Address


def add_driver(db_connection):
    with db_connection.transaction:
        drivers = Driver.create(
            {'first_name': 'John', 'last_name': 'Doe', 'employee_status': 'P'},
            {'first_name': 'Jane', 'last_name': 'Doe', 'employee_status': 'V'},
            {'first_name': 'Alexander', 'last_name': 'Ortega', 'employee_status': 'V'},
            {'first_name': 'Rahul', 'last_name': 'Martinez', 'employee_status': 'V'},
            {'first_name': 'Martin', 'last_name': 'Cordova', 'employee_status': 'P'},
            {'first_name': 'Mark', 'last_name': 'Fernandez', 'employee_status': 'V'},
            {'first_name': 'Shaine', 'last_name': 'Alenin', 'employee_status': 'V'},
            {'first_name': 'Thurston', 'last_name': 'Wayon', 'employee_status': 'V'},
            {'first_name': 'Darnall', 'last_name': 'Frear', 'employee_status': 'P'},
            {'first_name': 'Ronalda', 'last_name': 'Carlyon', 'employee_status': 'V'},
            {'first_name': 'Blakeley', 'last_name': 'Gunby', 'employee_status': 'P'},
            {'first_name': 'Yorke', 'last_name': 'Hartington', 'employee_status': 'V'},
            {'first_name': 'Ryann', 'last_name': 'Britcher', 'employee_status': 'V'},
            {'first_name': 'Adamo', 'last_name': 'Paxton', 'employee_status': 'P'},
            {'first_name': 'Kristoffer', 'last_name': 'Pagan', 'employee_status': 'P'},
            {'first_name': 'Trevor', 'last_name': 'Ollin', 'employee_status': 'V'}
        )
    return drivers


def add_locations(db_connection):
    with db_connection.transaction:
        locations = Address.create(
            {'address': '5545 Center St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68106, 'is_center': True},
            {'address': '9029 Burt St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68114},
            {'address': '9110 Maplewood Blvd', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68134},
            {'address': '9715 Ohern Plz', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68127},
            {'address': '8170 Browne St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68134},
            {'address': '6705 S 85th St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68127},
            {'address': '6795 Emmet St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68104},
            {'address': '7115 N 50th Ave', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68152},
            {'address': '7205 N 73rd Plaza Cir', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68122},
            {'address': '7350 Graceland Dr', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68134},
            {'address': '4550 Walnut St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68106},
            {'address': '15423 Lloyd St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68144},
            {'address': '12205 Farnam St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68154},
            {'address': '2117 S 38th St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68105},
            {'address': '1019 S 106th Plz', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68114},
            {'address': '11679 Fowler Ave', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68164},
            {'address': '7909 Grover St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68124},
            {'address': '530 Loveland Dr', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68114},
            {'address': '1875 S 75th St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68124},
            {'address': '14455 Harrison St', 'city': 'Omaha', 'state': 'NE', 'zipcode': 68138}
        )
    return locations


def add_availability(db_connection):
    with db_connection.transaction:
        days = Availability.create(
            {'day': 'Mon'},
            {'day': 'Tue'},
            {'day': 'Wed'},
            {'day': 'Thu'},
            {'day': 'Fri'},
            {'day': 'Sat'},
            {'day': 'Sun'},
        )
    return days


if __name__ == '__main__':
    config.DATABASE_URL = settings.NEOMODEL_NEO4J_BOLT_URL
    db.set_connection(url=config.DATABASE_URL)

    print(db.url)

    print('Adding drivers to db')
    all_drivers = add_driver(db_connection=db)

    print('Adding locations to db')
    all_locations = add_locations(db_connection=db)

    print('Setting days')
    all_days = add_availability(db_connection=db)

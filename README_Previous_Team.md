# Team Fast Backend
This project's goal is to create a framework that has been designed to efficiently route delivery drivers coming from a single location. It also provides an easy-to-use interface (on the frontend) for managers that create routes, as well as the drivers that deliver using those routes. 

## Milestone 1: Release Notes
Many of the backend features are currently still in development. Right now all of the models are working in the database and we have begun work on the serializers and views. The serializers will be able to transform python objects to JSON and vice versa. The views will handle our API routes and the type of request (get, post, put, etc.).

Currently, our only working API route is `/locations/`

## Milestone 2: Release Notes

### Routing algorithm:
We wrote much of the API to communicate with external APIs and retrieve geocode and distance/duration matrices. We also set up a graph database using neo4j. One of our objectives was to be able to query a database and retrieve distance/duration between any pair of locations that are not new, thus saving on API. Then, we started implementing a modified version of Clarke and Wright's Savings algorithm with Time Window.

### Backend:
For Milestone 2 we have finished all of our API endpoints except for `/route/` post requests. All other views and serializers have been completed.

## Milestone 3: Release Notes

### Routing algorithm:
For this release, we finished writing 90% of the routing algorithm. We tested features we coded for milestone 2 (using the graph database, geocoding locations, and retrieving distance/duration matrices). We also added the logic to build routes, aka assign locations to drivers available to deliver, under different business constraints.

### Backend:
For Milestone 3, we made small changes to the client and driver models and got the `/route/` api endpoint ready for connection to the routing algorithm app.

## Milestone 4: Release Notes

### Routing algorithm:
The most essential aspects of the routing algorithm are implemented at this point. We unit-tested all of the non-basic classes of the routing algorithm and connected the routing algorithm to the other half of the backend. We also installed neo4j on AWS and got ready for deployment.

### Backend:
For Milestone 4, we have completed the bulk uploading of clients and drivers. We have edited their models and made a few changes based on feedback from Dr. Vitor and compatibility with the routing app.

## Milestone 5: Release Notes

### Routing algorithm:
We tested the routing algorithm with real-data and fixed bugs as we encounter them. We've documented some of the code. Documentation still needs to be added to a couple of files.

### Backend:
For Milestone 5, we finished linking our routing app and the main backend for api requests. In doing so, we added a new model: route_list. A route_list has a one to many relation with routes, so that we know what routes are generated together. We ran into issues with Django's Rest Framework Serializers. Having multiple nested serializers caused issues with the relations between the route_list, route, and client models. This was solved by saving the itinerary(clients) as JSON in the database. An added bonus to this structure, meant it was easy to keep the order of the itinerary.

# Installation
## Install and update Python

## Create a virtual environment
`python3 -m venv venv`

### For windows:
`python -m venv venv`

## Start virtual environment
### For linux/mac/git bash
`. venv/bin/activate`

### For windows:
`venv\Scripts\activate`

## Install/Upgrade pip
`python -m pip install --upgrade pip`

## Install packages
`pip install -r requirements.txt`

## Download/Install Postgres
https://www.postgresql.org/download/

### Create database
`psql -U postgres`
Then enter in your password. (You may have to add postgres to your path variable)

Create the database
`CREATE DATABASE fastDB;` you can then quit with `exit;`

## Copy settings
`cp backend/settings.example backend/settings.py`

Change password in `settings.py` to same password used in Postgres installation

## Make Migrations
`python manage.py makemigrations backend`

Then

`python manage.py migrate backend`

## Create superuser
`python manage.py createsuperuser`

May have to use `winpty python manage.py createsuperuser`


## Test Deployment command

`python manage.py runserver 0.0.0.0:8000`

## Team-2Fast2Furious-backend  

As noted by Team-Fast's README file, this project seeks to implement a route generation service for the Intercultural Senior Center to help them create routes for their delivery drivers. Our team, Team 2Fast2Furious, aims to build on on the work of the Team-Fast. To run this application, view the README.  

## Milestone 1 Release Notes  

We have adjusted the backend enviroment to start on this project: 
- Updating Chromedriver to version 98
- Set up our own Postgresql and neo4j databases
- Added missing dependencies, django-cors-headers~=3.11.0, into requirements.txt
- Set IPs to local testing enviroment
- Created and added our own Bing API Key
- Updated settings.py to match our changes
- Ran testing suite to make sure app was functioning correctly
- Starting implementing caching savings between location for faster algorithm performance
- Updated installation instructions

We still do not have the caching for savings working.

## Installing
1. Clone this git repo `git clone https://github.com/Atari4800/fast-backend.git`
1. Set up virtual enviroment `python -m venv .venv
2. Install dependencies `pip install -r requirements.txt`
3. Install postgres https://www.postgresql.org/download/ or pgAdmin4
4. Change database password in settings.py to same password used in Postgres installation
5. Make migrations `python manage.py makemigrations`
6. Migrate into database `python manage.py migrate`
7. Install neo4j Community Edition https://neo4j.com/download-center/
8. Open up terminal and navigate to `<Install Location>/neo4j-community-4.4.3\bin`
9. Run `neo4j console` to start neo4j server
10. Open up another terminal and navigate to backend repo root
11. Run `python manage.py runserver` to start django server
12. Continue to installation instructions on frontend READMEmd

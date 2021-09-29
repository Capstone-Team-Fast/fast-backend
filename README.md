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
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

## Copy settings
`cp backend/settings.example backend/settings.py`

Change password in `settings.py` to same password used in Postgres installation

## Create superuser
`python manage.py createsuperuser`

May have to use `winpty python manage.py createsuperuser`
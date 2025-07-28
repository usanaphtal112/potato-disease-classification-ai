#!/bin/bash

echo "--------------START BUILD-----------"

echo "Building Project Packages........"
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

echo "Collect static files"
python3.9 manage.py collectstatic --noinput

echo "Migrating the Databases........."
# python3 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "--------------END OF BUILD-----------"

#!/bin/bash

echo "--------------START BUILD-----------"

# Check if pip3 is available
if command -v pip3 &> /dev/null; then
    echo "pip3 is installed. Version:"
    pip3 --version
else
    echo "pip3 is not installed"
fi

echo "Building Project Packages........"
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt

echo "Collect static files"
python3.9 manage.py collectstatic --noinput

echo "Migrating the Databases........."
# python3 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

echo "--------------END OF BUILD-----------"

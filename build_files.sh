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
python3.12 -m pip install --upgrade pip
pip3.12 install -r requirements.txt

echo "Migrating the Databases........."
# python3 manage.py makemigrations --noinput
python3.12 manage.py migrate --noinput

echo "Collect static files"
python3.12 manage.py collectstatic --noinput

echo "--------------END OF BUILD-----------"
#!/bin/bash


set -o erexit

# Install the required packages
pip install -r requirements.txt

# Initialize the database
flask db init

# Run database migrations
flask db migrate


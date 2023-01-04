#!/bin/bash

apt-get install sudo
# Install Python 3.9
sudo apt-get update
sudo apt-get install python3.9

# Create a virtual environment
python3.9 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Initialize the database
flask db init

# Run database migrations
flask db migrate

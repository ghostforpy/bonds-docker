#!/bin/bash
sudo docker-compose -f production.yml run --rm django python manage.py migrate

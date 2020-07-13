#!/bin/bash
docker-compose -f production.yml run --rm django python manage.py makemigrations

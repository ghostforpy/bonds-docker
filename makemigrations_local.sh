#!/bin/bash
docker-compose -f local.yml run --rm django python manage.py makemigrations

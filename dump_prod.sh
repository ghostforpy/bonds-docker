#!/bin/bash
sudo docker-compose -f production.yml run --rm django python manage.py dumpdata --exclude auth.permission --exclude contenttypes > db.json

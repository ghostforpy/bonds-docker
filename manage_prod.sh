#!/bin/bash
docker-compose -f production.yml run --rm django ./manage.py $@

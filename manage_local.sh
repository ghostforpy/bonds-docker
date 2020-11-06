#!/bin/bash
docker-compose -f local.yml run --rm django ./manage.py $@

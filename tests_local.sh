#!/bin/bash
docker-compose -f local.yml run --rm django pytest $1

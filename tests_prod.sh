#!/bin/bash
sudo docker-compose -f production.yml run --rm django pytest $1

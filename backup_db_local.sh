#!/bin/bash
t=`docker ps | grep postgres`
IFS=' ' read -ra my_array <<< "$t"
docker_id=$my_array
IFS="'" read -ra my_array2 <<< `docker-compose -f local.yml exec postgres backup | grep SUCCESS`
backup_id=${my_array2[3]}
docker cp $docker_id:/backups/$backup_id ./backups/

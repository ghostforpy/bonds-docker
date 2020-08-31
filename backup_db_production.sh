#!/bin/bash
t=`sudo docker ps | grep postgres`
IFS=' ' read -ra my_array <<< "$t"
docker_id=$my_array
IFS="'" read -ra my_array2 <<< `sudo docker-compose -f production.yml exec postgres backup | grep SUCCESS`
backup_id=${my_array2[3]}
sudo docker cp $docker_id:/backups/$backup_id ../backups/

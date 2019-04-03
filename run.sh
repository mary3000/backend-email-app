#!/usr/bin/env bash
sudo kill $(sudo lsof -i:15672 -t)
sudo kill $(sudo lsof -i:5672 -t)
sudo docker-compose up $1
#!/bin/bash

docker compose up --build -d --remove-orphans
docker compose exec kali /bin/bash
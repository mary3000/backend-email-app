#!/usr/bin/env bash

sleep 10

flask db init
flask db migrate
flask db upgrade
python app.py
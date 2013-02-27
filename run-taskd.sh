#!/bin/bash

cd /data/srv/LambdaCast/
source .venv/bin/activate
python manage.py taskd start

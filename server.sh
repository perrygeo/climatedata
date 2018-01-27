#!/bin/bash
source /home/mperry/venv/climatedata/bin/activate
gunicorn -w 8 -b 127.0.0.1:5000 app:app

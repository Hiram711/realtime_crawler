#! /bin/bash
flask init
uwsgi --http :5000 --wsgi-file wsgi.py --callable app  --processes 4 --threads 2
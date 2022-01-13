#! /bin/sh

python -m pip install -r requirements.txt
# Uncomment for verbose mode
python -m kopf run app.py --verbose --liveness=http://0.0.0.0:8080/healthz
# python -m kopf run app.py
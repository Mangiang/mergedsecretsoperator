#! /bin/sh

python -m pip install -r requirements.txt
# Uncomment for verbose mode
# python -m kopf run app.py --verbose
python -m kopf run app.py
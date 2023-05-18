#!/bin/bash
cd "$(dirname "$0")"

python3 -u sequencing.py > update.log
python3 -u pride.py >> update.log
python3 -u flowrepository.py >> update.log
python3 -u create_json.py >> update.log
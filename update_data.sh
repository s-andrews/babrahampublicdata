#!/bin/bash
cd "$(dirname "$0")"

python3 sequencing.py > update.log
python3 pride.py >> update.log
python3 create_json >> update.log
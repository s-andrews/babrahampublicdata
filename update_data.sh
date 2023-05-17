cd "$(dirname "$0")"

python sequencing.py > update.log
python pride.py >> update.log
python create_json >> update.log
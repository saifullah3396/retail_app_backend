SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH/..
python manage.py makemigrations users
python manage.py makemigrations organizations
python manage.py makemigrations locations
python manage.py makemigrations measurement_frames
python manage.py makemigrations cameras
python manage.py makemigrations deepstream_servers
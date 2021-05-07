SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH/..
USER_NAME=admin
EMAIL=admin@admin.com
python manage.py createsuperuser --username $USER_NAME --email $EMAIL
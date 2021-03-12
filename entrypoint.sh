export DJANGO_DATABASE_URL=$(heroku config:get DATABASE_URL -a retail-irl-ncai)
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py setup_apps
gunicorn backend.wsgi --bind 0.0.0.0:8000
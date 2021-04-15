# Generic Python DJango Backend

## Getting started:

### Virtual Environment Installation:

Install virtual environment wrapper:

```
pip install virtualenvwrapper
```

Setup a new virtual environments root directory and initialize virtualenvwrapper:

```
export WORKON_HOME=~/.virtual_envs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
```

Add virtualenvwrapper initialization at terminal startup:

```
echo 'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bashrc
```

Create a new virtual environment with the name `django-backend` with python3. The name can be chosen by the user:

```
mkvirtualenv django-backend --python=3
workon django-backend
```

Install project dependencies:

```
pip3 install -r requirements.txt
```

### Postgresql Database (Ubuntu 18.04):

Install Postgresql database in your system.

```
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Login to base postgresql user:

```
sudo -i -u postgres
```

Create a new user for development:

```
createuser --interactive

Output:
Enter name of role to add: admin
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) y
Shall the new role be allowed to create more new roles? (y/n) n
```

Create a new database:

```
createdb retail_db
```

Update the postgresql configuration for the new user by adding the following line to `pg_hba.conf` file in `/etc/postgresql/`.

```
local   all             admin                 trust
```

Restart the postgresql server:

```
sudo service postgresql restart
```

### DJango Database Settings:

Update the `DATABASE` variable in `backend/settings.py` as follows:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'retail_db',
        'USER': 'admin',
    }
}
```

Update the database according to database settings in django:

```
python manage.py migrate
```

### Run DJango Server:

```
python manage.py runserver
```

## DJango Admin:

Create a new django admin user

```
python manage.py createsuperuser
```

You should use the following configuration:

```
Username: admin
Email address: admin@admin.com
Password:
Password (again):
The password is too similar to the username.
This password is too short. It must contain at least 8 characters.
This password is too common.
Bypass password validation and create user anyway? [y/N]: y
Superuser created successfully.
```

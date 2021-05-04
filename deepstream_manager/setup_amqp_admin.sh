# Sets up the rabbitmq user for our application
rabbitmqctl add_user retail_django_admin admin
rabbitmqctl set_user_tags retail_django_admin administrator
rabbitmqctl set_permissions -p / retail_django_admin ".*" ".*" ".*"
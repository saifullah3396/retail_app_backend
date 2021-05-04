# Sets up the rabbitmq vhost for our application. This is currently not used
# since deepstream uses default '/' vhost while sending messages to queues.
# rabbitmqctl add_vhost retail_django_server
# rabbitmqctl set_vhost_limits -p retail_django_server '{"max-connections": -1}'
# rabbitmqctl set_vhost_limits -p retail_django_server '{"max-queues": 1024}'
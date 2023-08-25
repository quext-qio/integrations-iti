
import os
import json

config = {
    'user_name': os.environ['YARDI_USER_NAME'],
    'password': os.environ['YARDI_PASSWORD'],
    'server_name': os.environ['YARDI_SERVER_NAME'],
    'database': os.environ['YARDI_DATABASE'],
    'interface_license': os.environ['YARDI_INTERFACE_LICENSE'],
    'user_name_demo': os.environ['YARDI_USER_NAME_DEMO'],
    'password_demo': os.environ['YARDI_PASSWORD_DEMO'],
    'server_name_demo': os.environ['YARDI_SERVER_NAME_DEMO'],
    'database_demo': os.environ['YARDI_DATABASE_DEMO'],
    'interface_license_demo': os.environ['YARDI_INTERFACE_LICENSE_DEMO'],
    'leasing_url': os.environ['LEASING_HOST'],
    'ips_host': os.environ['IPS_HOST'],
    'yardi_url': os.environ['YARDI_URL'],
    'yardi_url_demo': os.environ['YARDI_URL_DEMO']
}
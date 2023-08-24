
import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    'user_name': parameter_store['YARDI_USER_NAME'],
    'password': parameter_store['YARDI_PASSWORD'],
    'server_name': parameter_store['YARDI_SERVER_NAME'],
    'database': parameter_store['YARDI_DATABASE'],
    'interface_license': parameter_store['YARDI_INTERFACE_LICENSE'],
    'user_name_demo': parameter_store['YARDI_USER_NAME_DEMO'],
    'password_demo': parameter_store['YARDI_PASSWORD_DEMO'],
    'server_name_demo': parameter_store['YARDI_SERVER_NAME_DEMO'],
    'database_demo': parameter_store['YARDI_DATABASE_DEMO'],
    'interface_license_demo': parameter_store['YARDI_INTERFACE_LICENSE_DEMO'],
    'leasing_url': parameter_store['LEASING_HOST'],
    'ips_host': parameter_store['IPS_HOST'],
    'yardi_url': parameter_store['YARDI_URL'],
    'yardi_url_demo': parameter_store['YARDI_URL_DEMO']
}
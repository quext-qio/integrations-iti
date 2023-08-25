import os
import json

config = {
    'api_key': os.environ['ENGRAIN_API_KEY'],
    'quext_api_key': os.environ['ENGRAIN_QUEXT_API_KEY'],
    'madera_uuid': os.environ['ENGRAIN_MADERA_UUID'],
    'current_env': os.environ['CURRENT_ENV'],
    "newco_host": os.environ['NEWCO_DB_HOST'],
    "newco_password": os.environ['NEWCO_DB_PASSWORD'],
    "newco_db_name": os.environ['NEWCO_DB_NAME'],
    "newco_db_user": os.environ['NEWCO_DB_USER'],
}
import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))

config = {
    'api_key': parameter_store['ENGRAIN_API_KEY'],
    'quext_api_key': parameter_store['ENGRAIN_QUEXT_API_KEY'],
    'madera_uuid': parameter_store['ENGRAIN_MADERA_UUID'],
    'current_env': parameter_store['CURRENT_ENV'],
    "newco_host": parameter_store['NEWCO_DB_HOST'],
    "newco_password": parameter_store['NEWCO_DB_PASSWORD'],
    "newco_db_name": parameter_store['NEWCO_DB_NAME'],
    "newco_db_user": parameter_store['NEWCO_DB_USER'],
}
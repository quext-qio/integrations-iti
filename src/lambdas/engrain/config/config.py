import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))

config = {
    'api_key': parameter_store['ENGRAIN_API_KEY'],
    'quext_api_key': parameter_store['ENGRAIN_QUEXT_API_KEY'],
    'madera_uuid': parameter_store['ENGRAIN_MADERA_UUID'],
    'current_env': parameter_store['CURRENT_ENV'],
}
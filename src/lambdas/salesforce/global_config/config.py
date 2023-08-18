import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
salesforce_config = {
    'username': parameter_store['SALESFORCE_USERNAME'],
    'password': parameter_store['SALESFORCE_PASSWORD'],
    'security_token': parameter_store['SALESFORCE_SECURITY_TOKEN'],
    'current_env': parameter_store['CURRENT_ENV'],
}
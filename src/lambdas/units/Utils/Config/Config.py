import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    "Integration_partner_id": parameter_store['RESMAN_INTEGRATION_PARTNER_ID'],
    "ApiKey": parameter_store['RESMAN_API_KEY'],
    "Newco_host": parameter_store['NEWCO_DB_HOST'],
    "Newco_password": parameter_store['NEWCO_DB_PASSWORD'],
    "Newco_db_name": parameter_store['NEWCO_DB_NAME'],
    "Newco_db_user": parameter_store['NEWCO_DB_USER'],
} 
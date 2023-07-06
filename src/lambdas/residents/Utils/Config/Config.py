import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    "Newco_host": parameter_store['NEWCO_DB_HOST'],
    "Newco_password": parameter_store['NEWCO_DB_PASSWORD'],
    "Newco_db_name": parameter_store['NEWCO_DB_NAME'],
    "Newco_db_user": parameter_store['NEWCO_DB_USER'],
} 
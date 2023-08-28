import os

config = {
    "Integration_partner_id": os.environ['RESMAN_INTEGRATION_PARTNER_ID'],
    "ApiKey": os.environ['RESMAN_API_KEY'],
    "Newco_host": os.environ['NEWCO_DB_HOST'],
    "Newco_password": os.environ['NEWCO_DB_PASSWORD'],
    "Newco_db_name": os.environ['NEWCO_DB_NAME'],
    "Newco_db_user": os.environ['NEWCO_DB_USER'],
    "Engrain_host": os.environ['ENGRAIN_HOST'],
    "Engrain_api_key": os.environ['ENGRAIN_API_KEY'],  
} 
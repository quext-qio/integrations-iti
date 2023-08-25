import os
import json

config = {
    "Newco_host": os.environ['NEWCO_DB_HOST'],
    "Newco_password": os.environ['NEWCO_DB_PASSWORD'],
    "Newco_db_name": os.environ['NEWCO_DB_NAME'],
    "Newco_db_user": os.environ['NEWCO_DB_USER'],
} 
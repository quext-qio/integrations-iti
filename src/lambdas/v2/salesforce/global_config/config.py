import os
import json

salesforce_config = {
    'username': os.environ['SALESFORCE_USERNAME'],
    'password': os.environ['SALESFORCE_PASSWORD'],
    'security_token': os.environ['SALESFORCE_SECURITY_TOKEN'],
    'current_env': os.environ['CURRENT_ENV'],
}
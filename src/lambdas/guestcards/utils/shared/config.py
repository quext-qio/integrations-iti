import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    #Yardi
    'user_name': parameter_store['YARDI_USER_NAME'],
    'password': parameter_store['YARDI_PASSWORD'],
    'server_name': parameter_store['YARDI_SERVER_NAME'],
    'database': parameter_store['YARDI_DATABASE'],
    'interface_license': parameter_store['YARDI_INTERFACE_LICENSE'],
    'leasing_url': parameter_store['LEASING_HOST'],
    'yardi_url': parameter_store['YARDI_URL'],
    #Resman
    "Integration_partner_id": parameter_store['RESMAN_INTEGRATION_PARTNER_ID'],
    "resman_account_id": parameter_store['RESMAN_ACCOUNT_ID'],
    "resman_property_id": parameter_store['RESMAN_PROPERTY_ID'],
    "ApiKey": parameter_store['RESMAN_API_KEY'],
    "quext_host": parameter_store['QXT_CALENDAR_TOUR_HOST'],
}
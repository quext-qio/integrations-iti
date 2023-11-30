import os
from host.url_handler import UrlHandler

# It handles the host depend of stage
UrlHandler = UrlHandler(os.environ['CURRENT_ENV'])


config = {
    #Yardi
    'user_name': os.environ['YARDI_USER_NAME'],
    'password': os.environ['YARDI_PASSWORD'],
    'server_name': os.environ['YARDI_SERVER_NAME'],
    'database': os.environ['YARDI_DATABASE'],
    'interface_license': os.environ['YARDI_INTERFACE_LICENSE'],
    'leasing_url': UrlHandler.get_leasing_host(),
    'yardi_url': UrlHandler.get_yardi_host(),
    #Resman
    "Integration_partner_id": os.environ['RESMAN_INTEGRATION_PARTNER_ID'],
    "resman_account_id": os.environ['RESMAN_ACCOUNT_ID'],
    "resman_property_id": os.environ['RESMAN_PROPERTY_ID'],
    "ApiKey": os.environ['RESMAN_API_KEY'],
    "quext_host": os.environ['QXT_CALENDAR_TOUR_HOST'],
}
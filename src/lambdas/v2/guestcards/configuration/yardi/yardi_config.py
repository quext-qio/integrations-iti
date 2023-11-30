import os
from host.url_handler import UrlHandler

# It handles the host depend of stage
UrlHandler = UrlHandler(os.environ['CURRENT_ENV'])

# Config for Yardi
config = {
    'user_name': os.environ['YARDI_USER_NAME'],
    'password': os.environ['YARDI_PASSWORD'],
    'server_name': os.environ['YARDI_SERVER_NAME'],
    'database': os.environ['YARDI_DATABASE'],
    'interface_license': os.environ['YARDI_INTERFACE_LICENSE'],
    'leasing_url': UrlHandler.get_leasing_host(),
    'ips_host': UrlHandler.get_ips_host(),
    'yardi_url': UrlHandler.get_yardi_host(),
}
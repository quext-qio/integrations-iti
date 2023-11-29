import os
from host.base_url import BaseUrl

# It handles the host depend of stage
BaseUrl = BaseUrl(os.environ['CURRENT_ENV'])

# Config for Yardi
config = {
    'user_name': os.environ['YARDI_USER_NAME'],
    'password': os.environ['YARDI_PASSWORD'],
    'server_name': os.environ['YARDI_SERVER_NAME'],
    'database': os.environ['YARDI_DATABASE'],
    'interface_license': os.environ['YARDI_INTERFACE_LICENSE'],
    'leasing_url': os.environ['LEASING_HOST'],
    'ips_host': BaseUrl.get_ips_host(),
    'yardi_url': os.environ['YARDI_URL'],
}
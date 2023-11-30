import os
from host.url_handler import UrlHandler

# It handles the host depend of stage
UrlHandler = UrlHandler(os.environ['CURRENT_ENV'])

config = {
    'auth_host': UrlHandler.get_auth_host(),
} 
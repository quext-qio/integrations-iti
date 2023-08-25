import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
placepay_config = {
    'ApiKey': os.environ.get['PLACE_PAY_API_KEY'],
} 
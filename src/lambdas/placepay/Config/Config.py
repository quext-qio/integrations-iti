import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
config = {
    'ApiKey': parameter_store['PLACE_PAY_API_KEY'],
} 
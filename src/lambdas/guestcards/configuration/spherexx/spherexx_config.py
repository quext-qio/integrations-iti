
import os
import json

parameter_store = json.loads(os.environ.get("parameter_store"))
spherexx_config = {
    "spherexx_username": parameter_store['SPHEREXX_USERNAME'],
    "spherexx_password": parameter_store['SPHEREXX_PASSWORD']
}


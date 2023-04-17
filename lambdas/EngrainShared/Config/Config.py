import os

config = {
    'api_key': os.environ['ENGRAIN_API_KEY'],
    'quext_api_key': os.environ['ENGRAIN_QUEXT_API_KEY'],
    'madera_uuid': os.environ['ENGRAIN_MADERA_UUID'],
    'current_env': os.environ['CURRENT_ENV'],
}
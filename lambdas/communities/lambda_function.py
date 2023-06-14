import json
from DataPushPullShared.DataController import DataController
#from cerberus import Validator

def lambda_handler(event, context):
    return {
        'headers': {
            'Content-Type': 'application/json'
        },
        'statusCode': 200,
        'body': {
            'data': DataController.get_communities(event["customerUUID"]),
            'errors': []
        },
    }
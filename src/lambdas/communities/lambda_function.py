import json
from DataPushPullShared.DataController import DataController
#from cerberus import Validator

def lambda_handler(event, context):
    input = json.loads(event['body'])
    code, data_controller = DataController("info").get_communities(input.get("customerUUID",""))
    return {
        'statusCode': code,
        'body':  json.dumps(data_controller),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
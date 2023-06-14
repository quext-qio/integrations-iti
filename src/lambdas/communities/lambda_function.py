import json
from DataPushPullShared.DataController import DataController
#from cerberus import Validator

def lambda_handler(event, context):
    input = json.loads(event['body'])
    data_controller = DataController("info")
    return {
        'statusCode': "500",
        'body': json.dumps({
            'data': data_controller.get_communities(input["customerUUID"]),
            'errors': []
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
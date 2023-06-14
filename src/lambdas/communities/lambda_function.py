import json
#from DataPushPullShared.DataController import DataController
#from cerberus import Validator

def lambda_handler(event, context):
    return {
        'statusCode': "500",
        'body': json.dumps({
            'data': event['body'],
            'errors': []
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
import json
from DataPushPullShared.DataController import DataController

def lambda_handler(event, context):

    input = event['body']
    input = json.loads(input) if input else {}
    
    code, data_controller = DataController("info").get_customers(input.get("customerUUID",""))
    return {
        'statusCode': code,
        'body':  json.dumps(data_controller),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
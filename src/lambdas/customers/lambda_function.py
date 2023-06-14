import json
from DataPushPullShared.DataController import DataController

def lambda_handler(event, context):

    input = event['body']
    input = json.loads(input) if input else {}
    
    data_controller = DataController("info")
    return {
        'statusCode': "500",
        'body': json.dumps({
            'data': data_controller.get_customers(input.get("customerUUID") if "customerUUID" in input else ''),
            'errors': []
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
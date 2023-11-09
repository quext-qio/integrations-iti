import json
from DataController.DataControllerFactory import DataControllerFactory

def lambda_handler(event, context):
    input = json.loads(event['body'])
    code, data = DataControllerFactory().create_data_controller(input)
    return {
        'statusCode': code,
        'body': json.dumps(data),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
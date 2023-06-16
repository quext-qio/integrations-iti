import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory

def lambda_handler(event, context):
    input = json.loads(event['body'])
    return {
        'statusCode': "200",
        'body': 
            DataControllerFactory().create_data_controller(input)
        ,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
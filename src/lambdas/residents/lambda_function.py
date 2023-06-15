import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory

def lambda_handler(event, context):
    input = json.loads(event['body'])
    return {
        'statusCode': "200",
        'body': json.dumps({
            DataControllerFactory().partner_response(input)
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
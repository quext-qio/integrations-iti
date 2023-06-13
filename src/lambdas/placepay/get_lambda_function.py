import place
import json
from Schemas.SchemaRequestPost import SchemaRequestPost
from Utils.Response import Response
from Config.Config import config

def lambda_handler(event, context):
    return {
        'statusCode': "500",
        'body': json.dumps({
            'data': event['queryStringParameters'],
            'errors': []
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
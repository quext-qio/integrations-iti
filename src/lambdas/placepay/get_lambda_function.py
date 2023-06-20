import place
import mysql.connector
import json
from Schemas.SchemaRequestPost import SchemaRequestPost
from Utils.Response import Response
from Config.Config import config

def lambda_handler(event, context):
    try:
        query_parameters = event['queryStringParameters']
        account_id = query_parameters["accountId"]

        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': account_id,
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
    except Exception as e:
        return {
            'statusCode': "500",
            'body': json.dumps({
                'data': [],
                'errors': f"{e}",
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
import place
import json
from schemas.schema_request_get import SchemaRequestGet
from config.config import config

def lambda_handler(event, context):
    query_params = event['queryStringParameters']
    is_valid, input_errors = SchemaRequestGet(query_params).is_valid()

    if is_valid:
        try:
            place.api_key = config['ApiKey']
            access_token = place.AccessToken.create(
                account_id = query_params["accountId"],
                type='session_access'
            )

            # Case: Success
            return {
                'statusCode': "200",
                'body': json.dumps({
                    'data': [
                        access_token.access_token
                    ],
                    'errors': []
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }
        
        except Exception as e:
            # Case: Unhandled error
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
        
    else:
        # Case: Bad Request
        errors = [{"message": f"{k}, {v[0]}" } for k,v in input_errors.items()]
        return {
            'statusCode': "400",
            'body': json.dumps({
                'data': [],
                'errors': errors,
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
import json
import place
from Schemas.SchemaRequestPost import SchemaRequestPost
from Config.Config import config

def lambda_handler(event, context):
    is_valid, input_errors = SchemaRequestPost(event).is_valid()
    if is_valid:
        try:
            place.api_key = f"{config['ApiKey']}"
            account = place.Account.create(
                email = event["email"],
                full_name = event["fullName"],
                user_type= event["userType"]
            )

            # Case: Success
            return {
                'statusCode': "200",
                'body': json.dumps({
                    'data': [account.__dict__['_obj']],
                    'errors': []
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }
        except Exception as e:
            # Case: Internal Server Error 
            print(f"Error in account creation: {e}, body of request: {event}")
            return {
                'statusCode': "500",
                'body': json.dumps({
                    'data': [],
                    'errors': [{"message": f"Internal Server Error"}],
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
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
                'statusCode': 200,
                'data': [account.__dict__['_obj']],
                'errors': []
            }
        except Exception as e:
            # Case: Internal Server Error 
            print(f"Error in account creation: {e}")
            return {
                'statusCode': 500,
                'data': [],
                'errors': [{"message": f"Internal Server Error"}],
            }
    else:
        # Case: Bad Request
        errors = [{"message": f"{k}, {v[0]}" } for k,v in input_errors.items()]
        return {
            'statusCode': 400,
            'data': [],
            'errors': errors
        }
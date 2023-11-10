import place
import json
from schemas.schema_request_post import SchemaRequestPost
from global_config.config import placepay_config
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) PlacePay Create Account Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    input = json.loads(event['body'])
    is_valid, input_errors = SchemaRequestPost(input).is_valid()
    if is_valid:
        try:
            place.api_key = f"{placepay_config['ApiKey']}"
            account = place.Account.create(
                email=input["email"],
                full_name=input["fullName"],
                user_type=input["userType"]
            )

            # Case: Success
            logger.info(f"Successfully created account: {account.__dict__['_obj']}")
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
            logger.critical(
                f"Error in account creation: {e}, body of request: {event}")
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
        errors = [{"message": f"{k}, {v[0]}"} for k, v in input_errors.items()]
        logger.warning(f"Bad Request: {errors}")
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

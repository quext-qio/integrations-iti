import json
#from cerberus import Validator

def lambda_handler(event, context):
    return {
        'headers': {
            'Content-Type': 'application/json'
        },
        'statusCode': 200,
        'body': {
            'data': "Hello from Lambda",
            'errors': []
        },
    }
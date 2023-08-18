import json
from schemas.schema_request_post import SchemaRequestPost
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from AccessControl import AccessUtils as AccessControl

def lambda_handler(event, context):
    # Validate input
    input = json.loads(event['body'])
    
    print(f"EVENT: {event}")
    try:
        # ACL Validation
        print(f"ACL Validation: {event['headers']}, type: {type(event['headers'])}")
        if 'x-api-key' not in event['headers']:
            print("No API key header.")
            return {
                'statusCode': "401",
                'body': json.dumps({
                    'data': [],
                    'errors': [{"message": "Unauthorized"}],
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False
            }
        
        wsgi_input = {
            'PATH_INFO': event['resource'],
            'REQUEST_METHOD': event["httpMethod"],
            'HTTP_X_API_KEY': event['headers']['x-api-key']
        }
        print(f"WSGI INPUT: {wsgi_input}")

        res, res_code= AccessControl.check_access_control(wsgi_input)
        print(f"ACL Validation Result: {res}, {res_code}")
        if res_code != 200:
            return res_code, res
    except Exception as e:
        print(f"ACL Validation Error: {str(e)}")
        pass

    # Validate body of request
    is_valid, input_errors = SchemaRequestPost(input).is_valid()
    if not is_valid:
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

    # Salesforce flow
    try:
        # Get config from parameter store
        username = salesforce_config['username']
        password = salesforce_config['password']
        security_token = salesforce_config['security_token']
        current_env = salesforce_config['current_env']
        
        # Salesforce connection
        sf = None
        if current_env == 'prod':
            sf = Salesforce(username=username, password=password, security_token=security_token)
        else:    
            sf = Salesforce(username=username, password=password, security_token=security_token, domain='test')

        # Execute query
        query_result = sf.query_all(input['query'])

        # Case: Success
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': query_result,
                'errors': [],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
    except Exception as e:
        return {
            'statusCode': "400",
            'body': json.dumps({
                'data': {},
                'errors': [str(e)],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
        

    
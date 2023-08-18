import json
from schemas.schema_request_post import SchemaRequestPost
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from AccessControl import AccessUtils as AccessControl
from acl import ACL

def lambda_handler(event, context):
    print(f"Event: {event}, context: {context}")
    
    # ---------------------------------------------------------------------------------------------
    # AccessControl
    # ---------------------------------------------------------------------------------------------

    # Check if API key is present
    if 'x-api-key' not in event['headers']:
        print("Unauthorized: No API key header.")
        return {
            'statusCode': "401",
            'body': json.dumps({
                'data': {},
                'errors': [{"message": "Unauthorized"}],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False
        }
    
    # Create WSGI input required for [AccessControl.check_access_control()]
    wsgi_input = {
        'PATH_INFO': event['resource'],
        'REQUEST_METHOD': event["httpMethod"],
        'HTTP_X_API_KEY': event['headers']['x-api-key']
    }
    print(f"Input for send to [AccessControl]: {wsgi_input}")

    endpoint = event['resource']
    method = event["httpMethod"]
    api_key = event['headers']['x-api-key']
    is_acl_valid, response_acl = ACL.check_permitions(endpoint, method, api_key)
    # Call AccessControl to validate API key
    # acl_response, acl_code= AccessControl.check_access_control(wsgi_input)
    # print(f"Result from [AccessControl]: {acl_code} = {acl_response}")

    # If AccessControl return error, we will return the error
    if not is_acl_valid:
        print(f"Unauthorized: {response_acl}")
        return {
            'statusCode': f"{response_acl.status_code}",
            'body': json.dumps({
                'data': {},
                'errors': [{"message": "Unauthorized"}],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False
        }

    # ---------------------------------------------------------------------------------------------
    # Body validation
    # ---------------------------------------------------------------------------------------------

    # Validate body of request
    input = event['body'] if 'body' in event else {}
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

    # ---------------------------------------------------------------------------------------------
    # Salesforce flow
    # ---------------------------------------------------------------------------------------------
    try:
        # Get config from parameter store to connect to Salesforce
        username = salesforce_config['username']
        password = salesforce_config['password']
        security_token = salesforce_config['security_token']
        current_env = salesforce_config['current_env']
        
        # Salesforce authentication
        salesforce = None
        if current_env == 'prod':
            salesforce = Salesforce(username=username, password=password, security_token=security_token)
        else:    
            salesforce = Salesforce(username=username, password=password, security_token=security_token, domain='test')

        # Execute query
        query_result = salesforce.query_all(input['query'])

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
        # Case: Internal Server Error
        print(f"Unhandled exception in [Salesforce flow]: {e}")
        return {
            'statusCode': "500",
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
        

    
import json
from schemas.schema_request_post import SchemaRequestPost
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from AccessControl import AccessUtils as AccessControl

def lambda_handler(event, context):
    # ACL Validation
    headers = event['headers']
    wsgi_input = {
        'PATH_INFO': event['resource'],
        'REQUEST_METHOD': "POST"
    }
    if 'x-api-key' in headers:
        wsgi_input['HTTP_X_API_KEY'] = headers['x-api-key']

    res, res_code= AccessControl.check_access_control(wsgi_input)
    if res_code != 200:
        return res_code, res

    # Validate input
    input = json.loads(event['body'])
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
                'data': None,
                'errors': [str(e)],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
        

    
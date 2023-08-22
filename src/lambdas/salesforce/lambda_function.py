import json
from schemas.schema_request_post import SchemaRequestPost
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from acl import ACL

def lambda_handler(event, context):
    print(f"Event: {event}, context: {context}")
    
    # ---------------------------------------------------------------------------------------------
    # AccessControl
    # ---------------------------------------------------------------------------------------------
    # TODO: Uncomment when ACL is ready for stage and prod
    # is_acl_valid, response_acl = ACL.check_permitions(event)
    # if not is_acl_valid:
    #     return response_acl

    # ---------------------------------------------------------------------------------------------
    # Body validation
    # ---------------------------------------------------------------------------------------------

    # Validate body of request
    input = json.loads(event['body'])
    is_valid, input_errors = SchemaRequestPost(input).is_valid()
    if not is_valid:
        # Case: Bad Request
        errors = [{"message": f"{k}, {v[0]}" } for k,v in input_errors.items()]
        return {
            'statusCode': "400",
            'body': json.dumps({
                'data': {},
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
        
        # Salesforce authentication ([stage], [rc] and [prod] will be connected to the real Salesforce)
        salesforce = None
        if current_env == 'stage' or current_env == 'rc' or current_env == 'prod':
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
        
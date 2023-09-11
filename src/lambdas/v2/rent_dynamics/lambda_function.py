import json
from acl import ACL
from schemas.schema_request_post import SchemaRequestPost

def lambda_handler(event, context):
    print(event)
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permitions(event, check_endpoints=False)
    if not is_acl_valid:
        return response_acl
    
    # Get path parameters and body
    path_parameters = event['pathParameters']
    body = json.loads(event['body'])
    
    # Validate body and path parameters
    all_params = {**path_parameters, **body}
    is_valid, input_errors = SchemaRequestPost(all_params).is_valid()
    if not is_valid:
        return {
            "statusCode": "400",
            "body": json.dumps({
                "data": {},
                "errors": input_errors
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  
            },
            "isBase64Encoded": False  
        }

    # Get path parameters
    customerUUID = path_parameters['customerUUID']
    action = path_parameters['action']
    communityUUID = path_parameters['communityUUID']

    # Get body
    move_in_date = body['move_in_date']
    move_out_date = body['move_out_date']
    
    
    # Validate path parameters

    return {
        "statusCode": "200",
        "body": json.dumps({
            "data": f"hello from rentdynamics {customerUUID}, {action}, {communityUUID}",
            "errors": []
        }),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  
        },
        "isBase64Encoded": False  
    }

import json
from schemas.schema_request_post import SchemaRequestPost
from factory.service_factory import ServiceFactory
from acl import ACL
from IPSController import IPSController

def lambda_handler(event, context):
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permitions(event, check_endpoints=False)
    if not is_acl_valid:
        return response_acl
    
    if "body" in event and event['body'] is not None:
        body = json.loads(event['body'])
    else:
        body = {}

    # Get parameter
    parameter = body.get('Parameter', None)
    
    # Validate body and path parameters
    is_valid, input_errors = SchemaRequestPost(body, parameter.lower()).is_valid()
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
    
    
    # Factory based on action
    return ServiceFactory.get_service(parameter).get_data(body)

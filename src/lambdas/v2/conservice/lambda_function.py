import json
from schemas.schema_request_post import SchemaRequestPost
from factory.service_factory import ServiceFactory
from constants.constants import Constants
from utils.shared.acl import ACL

def lambda_handler(event, context):
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permitions(event, check_endpoints=False)
    if not is_acl_valid:
        return response_acl
    
    if Constants.BODY in event and event[Constants.BODY] is not None:
        body = json.loads(event[Constants.BODY])
    else:
        body = {}

    # Get parameter
    parameter = body.get(Constants.PARAMETER, None)
    
    # Validate body and path parameters
    is_valid, input_errors = SchemaRequestPost(body, parameter.lower()).is_valid()
    if not is_valid:
        return {
            "statusCode": Constants.HTTP_GOOD_RESPONSE_CODE,
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
    
    
    #Get data from conservice outgoing
    
    return ServiceFactory.get_service(parameter).get_data(body)

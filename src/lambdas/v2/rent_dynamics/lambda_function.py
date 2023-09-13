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
    
    # Get path parameters and body
    path_parameters = event['pathParameters']
    if "body" in event and event['body'] is not None:
        body = json.loads(event['body'])
    else:
        body = {}

    # Get Action
    action = path_parameters['action']
    
    # Validate body and path parameters
    all_params = {**path_parameters, **body}
    is_valid, input_errors = SchemaRequestPost(all_params, action).is_valid()
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
    
    # Validate IPS
    #Call IPS to get community id
    communityUUID = path_parameters['communityUUID']
    customerUUID = path_parameters['customerUUID']
    purpose = "unitAvailability"
    
    code, ips_response =  IPSController().get_platform_data(communityUUID, customerUUID, purpose)
    ips_response = json.loads(ips_response.text)
    print(ips_response)

    if "platformData" not in ips_response:
        return {
            "statusCode": "400",
            "body": json.dumps({
                "data": {},
                "errors": [
                    {
                        "message": "IPS response does not contain platformData"
                    }
                ]
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  
            },
            "isBase64Encoded": False  
        }

    # Add community_id to body
    body["community_id"] = int(ips_response.get("platformData").get('communityID'))
    
    # Factory based on action
    return ServiceFactory.get_service(action).get_data(path_parameters, body)

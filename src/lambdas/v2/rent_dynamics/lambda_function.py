import json
from schemas.schema_request_post import SchemaRequestPost
from factory.service_factory import ServiceFactory
from acl import ACL
from IPSController import IPSController

def lambda_handler(event, context):
    print(event)
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permitions(event, check_endpoints=False)
    if not is_acl_valid:
        return response_acl
    
    # Get path parameters and body
    path_parameters = event['pathParameters']
    body = json.loads(event['body']) if "body" in event else {}
    
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

    # Validate IPS
    #Call IPS to get community id
    communityUUID = path_parameters['communityUUID']
    customerUUID = path_parameters['customerUUID']
    purpose = "unitAvailability"
    
    code, ips_response =  IPSController().get_platform_data(communityUUID, customerUUID, purpose)
    ips_response = json.loads(ips_response.text)

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

    # Get Action
    action = path_parameters['action']
    
    # Factory based on action
    return ServiceFactory.get_service(action).get_data(path_parameters, body)

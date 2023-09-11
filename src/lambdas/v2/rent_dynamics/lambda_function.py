import json
from acl import ACL
from schemas.schema_request_post import SchemaRequestPost
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

    # Get path parameters
    customerUUID = path_parameters['customerUUID']
    action = path_parameters['action']
    communityUUID = path_parameters['communityUUID']

    #Call IPS to get community id
    purpose = "unitAvailability"
    code, ips_response =  IPSController().get_platform_data(communityUUID, customerUUID, purpose)
    ips_response = json.loads(ips_response.text)
    
    if "platformData" not in ips_response:
        raise Exception("IPS response does not contain PlatformData")
    
    # Validate if platform in PlatformData
    if "platform" not in ips_response["platformData"]:
        raise Exception("IPS response does not contain platform")

    parameter = {'community_id': int(ips_response['platformData']['communityID'])}
    
    #If Dates in payload, add it to parameters
    if body:
        parameter.update(body)
    
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

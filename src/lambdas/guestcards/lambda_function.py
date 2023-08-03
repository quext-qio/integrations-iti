import json
from factory.service_factory import ServiceFactory
from schemas.schema_request_post import SchemaRequestPost
from IPSController import IPSController

def lambda_handler(event, context):
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

    # Get platform data from IPS
    platformData = input["platformData"]
    communityUUID = platformData["communityUUID"]
    customerUUID = platformData["customerUUID"]
    purpose = "guestCards"
    code, ips_response =  IPSController().get_platform_data(communityUUID, customerUUID, purpose)
    ips_response = json.loads(ips_response.text)
    
    # Validate status code
    if code != 200:
        raise Exception(f"IPS returned error code {code} with message {ips_response['message']}")

    # Validate if platformData in response
    if "platformData" not in ips_response:
        raise Exception("IPS response does not contain PlatformData")
    
    # Validate if platform in PlatformData
    if "platform" not in ips_response["platformData"]:
        raise Exception("IPS response does not contain platform")

    # Get service type name from IPS response
    service_type_name = ips_response["platformData"]["platform"]
    service = ServiceFactory.get_service(service_type_name)
    return service.get_data(input)
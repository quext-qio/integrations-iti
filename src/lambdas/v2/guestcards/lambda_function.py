import json
from factory.service_factory import ServiceFactory
from schemas.schema_request_post import SchemaRequestPost
from IPSController import IpsV2Controller
from acl import ACL
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) GuestCards Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    input = json.loads(event['body'])
    is_acl_valid, response_acl = ACL.check_permitions(event)
    if not is_acl_valid:
        return response_acl
    is_valid, input_errors = SchemaRequestPost(input).is_valid()
    if not is_valid:
        # Case: Bad Request
        errors = [{"message": f"{k}, {v[0]}"} for k, v in input_errors.items()]
        logger.warning(f"Bad Request: {errors}")
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
    code, ips_response = IpsV2Controller().get_platform_data(
        communityUUID, purpose)
    ips_response = ips_response.json()

    # Validate status code
    if code != 200:
        msg = f"IPS returned error code {code} with message {ips_response['message']}"
        logger.error(msg)
        raise Exception(msg)

    # Validate if platform data available in IPS response
    if ('purpose' not in ips_response or 'guestCards' not in ips_response['purpose'] or
            'partner_name' not in ips_response['purpose']['guestCards']):
        msg = f"IPS response does not contain platform for community {communityUUID}, customer {customerUUID}"
        logger.error(msg)
        raise Exception(msg)

    # Get service type name from IPS response
    service_type_name = ips_response['purpose']['guestCards']['partner_name']
    service = ServiceFactory.get_service(service_type_name)
    logger.info(f"Factory response: {service_type_name}")
    return service.get_data(input, ips_response, logger)

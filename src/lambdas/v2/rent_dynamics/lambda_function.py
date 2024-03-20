import json
from schemas.schema_request_post import SchemaRequestPost
from factory.service_factory import ServiceFactory
from acl import ACL
from IPSController import IpsV2Controller
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Rent Dynamics Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permissions(
        event, check_endpoints=False)
    if not is_acl_valid:
        logger.info(f"ACL is not valid: {response_acl}")
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
    is_valid, input_errors = SchemaRequestPost(
        all_params, action.lower()).is_valid()
    if not is_valid:
        logger.info(f"Bad request: {input_errors}")
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
    # Call IPS to get community id
    communityUUID = path_parameters['communityUUID']
    customerUUID = path_parameters['customerUUID']
    purpose = "unitAvailability"

    code, ips_response = IpsV2Controller().get_platform_data(
        communityUUID, purpose)
    ips_response = ips_response.json()

    # Validate if platform data available in IPS response
    if ('purpose' not in ips_response or 'unitAvailability' not in ips_response['purpose'] or
            'partner_name' not in ips_response['purpose']['unitAvailability']) or "params" not in ips_response or "communityID" not in ips_response["params"]:
        logger.warning(f"IPS response does not contain platformData")
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
    body["community_id"] = ips_response["params"]["communityID"]

    # Factory based on action
    return ServiceFactory.get_service(action, logger).get_data(path_parameters, body, logger)

import json
from schemas.schema_request_post import SchemaRequestPost
from factory.service_factory import ServiceFactory
from constants.constants import Constants
from acl import ACL
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Conservice Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    # Validate ACL
    is_acl_valid, response_acl = ACL.check_permitions(
        event, check_endpoints=False)
    if not is_acl_valid:
        logger.info(f"ACL not valid: {response_acl}")
        return response_acl

    if Constants.BODY in event and event[Constants.BODY] is not None:
        body = json.loads(event[Constants.BODY])
    else:
        body = {}

    # Get parameter
    parameter = body.get(Constants.PARAMETER, None)

    # Validate body and path parameters
    is_valid, input_errors = SchemaRequestPost(
        body, parameter.lower()).is_valid()
    if not is_valid:
        logger.warning(f"Bad Request: {input_errors}")
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

    # Get data from conservice outgoing
    return ServiceFactory.get_service(parameter, logger).get_data(body, logger)

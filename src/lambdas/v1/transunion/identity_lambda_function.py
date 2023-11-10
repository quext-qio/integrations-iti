import os
import json
import random
import string
import requests
from Utils.Identity import is_verify
from Utils.Identity import create_auth_encryption
from Utils.Identity import replace_body_content_transunion
from Utils.Constants import constants
from schemas.IdentitySchema import IdentitySchema
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) TransUnion Identity Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    payload = json.loads(event["body"])
    valid_schema = True
    input_error = []

    # TransUnion identity base url
    identity_url = os.environ["TRANSUNION_IDENTITY_HOST"]

    # verifies if the request is for verification or evaluation
    if is_verify(payload):
        valid_schema, input_error = IdentitySchema(payload).is_valid_verify()
        payload["ReferenceNumber"] = "".join(random.choices(
            string.ascii_uppercase + string.digits, k=8))
        identity_url = f"{identity_url}/Verify"
        logger.info(f"TransUnion Identity Verify URL: {identity_url}")
    else:
        valid_schema, input_error = IdentitySchema(payload).is_valid_evaluate()
        identity_url = f"{identity_url}/Evaluate"
        logger.info(f"TransUnion Identity Evaluate URL: {identity_url}")

    # payload provided is valid
    if valid_schema:
        try:
            # ------------- handles the authtentication creation ------------- #
            url = os.environ["TRANSUNION_AUTHENTICATION"]
            logger.info(f"Calling TransUnion Authentication API {url}")
            auth_response = requests.get(url)
            logger.info(
                f"TransUnion Authentication API response: {auth_response.status_code}, {auth_response}")
            auth_response = json.loads(auth_response.text)
            transunion_property_id_code = os.environ["TRANSUNION_PROPERTY_ID_CODE"]

            payload["OrganizationId"] = transunion_property_id_code
            payload = json.dumps(payload)

            auth_encryption = create_auth_encryption(
                payload, auth_response["Nonce"], auth_response["Timestamp"], transunion_property_id_code, os.environ["TRANSUNION_SECRET_KEY"])
            headers_auth = f'{constants["RESIDENT_ID"]}{transunion_property_id_code}:{auth_encryption}:{auth_response["Timestamp"]}:{auth_response["Nonce"]}'
            # creates the required headers for the request
            headers = {
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Allow-Methods": "POST, HEAD, OPTIONS",
                "Access-Control-Allow-Origin": "*",
                "Content-type": "application/json",
                "Accept": "application/json",
                "Authorization": headers_auth
            }

            # ------------- handles the TransUnion requests ------------- #
            logger.info(f"Calling TransUnion Identity API {identity_url}")
            identity_response = requests.post(
                identity_url,
                data=payload,
                headers=headers,
            )
            logger.info(
                f"TransUnion Identity API response: {identity_response.status_code}, {identity_response}")

            # succesful request
            if identity_response.status_code == constants["HTTP_GOOD_RESPONSE_CODE"]:
                logger.info(
                    f"Succesfully got TransUnion response: {identity_response.text}")
                return {
                    "statusCode": constants["HTTP_GOOD_RESPONSE_CODE"],
                    "body": json.dumps({
                        "data": json.loads(replace_body_content_transunion(identity_response.text)),
                        "errors": []
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "isBase64Encoded": False
                }
            else:
                # if TransUnion/requests returns an error
                logger.info(
                    f"TransUnion response error: {identity_response.text}")
                return {
                    "statusCode": identity_response.status_code,
                    "body": json.dumps({
                        "data": [],
                        "errors": json.loads(identity_response.text)
                    }),
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                    },
                    "isBase64Encoded": False
                }
        except Exception as e:
            # in case an error ocurred while doing the requests
            logger.error(f"Unhandled error getting TransUnion response: {e}")
            return {
                "statusCode": "500",
                "body": json.dumps({
                    "data": [],
                    "errors": [{"message": f"Internal Server Error"}],
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "isBase64Encoded": False
            }
    else:
        # payload provided is not valid
        logger.warning(f"Bad Request: {input_error}")
        return {
            "statusCode": constants["HTTP_BAD_REQUEST_CODE"],
            "body": json.dumps({
                "data": [],
                "errors": input_error,
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "isBase64Encoded": False
        }

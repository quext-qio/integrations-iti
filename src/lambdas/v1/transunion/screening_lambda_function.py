import json
import os
import requests

from Utils.Constants import constants
from Utils.Screening import structure_object_resident_screening_transunion
from Utils.Screening import clean_xml_transunion_screening_response
from Utils.Converter import Converter
from schemas.ScreeningSchema import ScreeningSchema
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) TransUnion Screening Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    payload = json.loads(event["body"])

    valid_schema, input_error = ScreeningSchema(payload).is_valid()

    if valid_schema:
        logger.info(f"Payload is valid")
        payload = structure_object_resident_screening_transunion(payload, os.environ["TRANSUNION_MEMBER_NAME"], os.environ["TRANSUNION_REPORT_PASSWORD"], os.environ[
                                                                 "TRANSUNION_PROPERTY_ID"], os.environ["TRANSUNION_SOURCE_ID"], os.environ["TRANSUNION_POST_BACK_URL"])
        converter = Converter(payload)
        payload = converter.json_to_xml()

        # creates the required headers for the request
        headers = {
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
            "Access-Control-Allow-Methods": "POST, HEAD, OPTIONS",
            "Access-Control-Allow-Origin": "*",
            "Content-type": "application/json",
            "Accept": "application/xml",
        }
        url = os.environ["TRANSUNION_REPORT_HOST"]

        logger.info(
            f"Calling TransUnion Screening API {url} with payload: {payload}")
        response = requests.post(
            url,
            data=payload,
            headers=headers,
        )
        logger.info(
            f"TransUnion Report API response: {response.status_code}, {response}")
        response = clean_xml_transunion_screening_response(response)
        response = converter.xml_to_dict(response)

        status_message = response["gateway"]["status"]["statusMessage"]

        if status_message == "Success":
            # gets the applicants from the TransUnion response
            applicants = response["gateway"]["application"]["applicants"]["applicant"]
            # checks if the applicant is an object (to verify if there's only 1 applicant)
            if isinstance(applicants, dict):
                # changes the applicant to be an array of objects instead of an object
                response["gateway"]["application"]["applicants"]["applicant"] = [
                    applicants]

            logger.info(f"Succesfully got TransUnion response: {response}")
            return {
                "statusCode": constants["HTTP_GOOD_RESPONSE_CODE"],
                "body": json.dumps({
                    "data": {"application": response["gateway"]["application"]},
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
            logger.warning(f"TransUnion response error: {status_message}")
            return {
                "statusCode": response["gateway"]["status"]["statusCode"],
                "body": json.dumps({
                    "data": {},
                    "errors": status_message
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                },
                "isBase64Encoded": False
            }
    else:
        # payload provided is not valid
        logger.info(f"Bad request: {input_error}")
        return {
            "statusCode": constants["HTTP_BAD_REQUEST_CODE"],
            "body": json.dumps({
                "data": {},
                "errors": input_error,
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "isBase64Encoded": False
        }

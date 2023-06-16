import json
import os
import requests

from Utils.Constants import constants
from Utils.Screening import structure_object_resident_screening_transunion
from Utils.Screening import clean_xml_transunion_screening_response
from Utils.Converter import Converter
from schemas.ScreeningSchema import ScreeningSchema

def lambda_handler(event, context):
    parameter_store = json.loads(os.environ.get("parameter_store"))
    payload = json.loads(event["body"])

    valid_schema, input_error = ScreeningSchema(payload).is_valid()

    if valid_schema:
        payload = structure_object_resident_screening_transunion(payload, parameter_store["TRANSUNION_MEMBER_NAME"], parameter_store["TRANSUNION_REPORT_PASSWORD"], parameter_store["TRANSUNION_PROPERTY_ID"], parameter_store["TRANSUNION_SOURCE_ID"], parameter_store["TRANSUNION_POST_BACK_URL"])
        converter = Converter(payload)
        payload = converter.json_to_xml()

        # creates the required headers for the request
        headers = {
            "Access-Control-Allow-Headers": "Authorization, Content-Type",
            "Access-Control-Allow-Methods": "POST, HEAD, OPTIONS",
            "Access-Control-Allow-Origin": "*",
            "Content-type":"application/json", 
            "Accept":"application/xml",
        }

        response = requests.post(parameter_store["TRANSUNION_REPORT_HOST"], data=payload, headers=headers)
        response = clean_xml_transunion_screening_response(response)
        response = converter.xml_to_dict(response)

        status_message = response["gateway"]["status"]["statusMessage"]

        if status_message == "Success":
            # gets the applicants from the TransUnion response
            applicants = response["gateway"]["application"]["applicants"]["applicant"]
            # checks if the applicant is an object (to verify if there's only 1 applicant)
            if isinstance(applicants, dict):
                # changes the applicant to be an array of objects instead of an object
                response["gateway"]["application"]["applicants"]["applicant"] = [applicants]

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
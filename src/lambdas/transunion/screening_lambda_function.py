import json
import os
import requests

from Utils.Constants import constants
from Utils.Screening import structure_object_resident_screening_transunion
from Utils.Screening import clean_xml_transunion_screening_response
from Utils.Converter import Converter
from schemas.ScreeningSchema import ScreeningSchema

def lambda_handler(event, context):
    print("inside lambda handler for screening")

    parameter_store = json.loads(os.environ.get("parameter_store"))
    payload = json.loads(event["body"])

    print(f"getting this payload: {payload}")

    valid_schema, input_error = ScreeningSchema(payload).is_valid()

    if valid_schema:
      print("schema is valid")

      # values come from the paramter store
      '''
        payload = structure_object_resident_screening_transunion(payload, "QuextTest", "5A$6z49999.WW.52023", "1c9ae49b", "1e", "https://zato.dev.quext.io/api/v1/screening/post-back")
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

        # value is from paramter store
        response = requests.post("https://crexternal.turss.com/gateway/creditapp.ashx", data=payload, headers=headers)
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
                      "data": json.loads({'application': response["gateway"]["application"]}),
                      "errors": []
                  }),
                  "headers": {
                      "Content-Type": "application/json",
                      "Access-Control-Allow-Origin": "*",  
                  },
                  "isBase64Encoded": False  
              }
              
        else:
            return {
                "statusCode": response["gateway"]["status"]["statusCode"],
                "body": json.dumps({
                    "data": [],
                    "errors": status_message
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",  
                },
                "isBase64Encoded": False  
            }
          '''

      return {
            "statusCode": "200",
            "body": json.dumps({
                "data": [],
                "errors": ["payload provided is valid"]
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  
            },
            "isBase64Encoded": False  
      }
    else:
        print("schema is NOT valid")

        # payload provided is not valid
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
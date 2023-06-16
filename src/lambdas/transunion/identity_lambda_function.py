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

def lambda_handler(event, context):
  parameter_store = json.loads(os.environ.get("parameter_store"))

  payload = json.loads(event["body"])
  valid_schema = True
  input_error = []
  
  # TransUnion identity base url
  identity_url = parameter_store["TRANSUNION_IDENTITY_HOST"]

  # verifies if the request is for verification or evaluation
  if is_verify(payload):
      valid_schema, input_error = IdentitySchema(payload).is_valid_verify()
      payload["ReferenceNumber"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
      identity_url = f"{identity_url}/Verify"
  else:
      valid_schema, input_error = IdentitySchema(payload).is_valid_evaluate()
      identity_url = f"{identity_url}/Evaluate"

  # payload provided is valid
  if valid_schema:
    try:
      # ------------- handles the authtentication creation ------------- #
      auth_response = requests.get(parameter_store["TRANSUNION_AUTHENTICATION"])
      auth_response = json.loads(auth_response.text)
      transunion_property_id_code = parameter_store["TRANSUNION_PROPERTY_ID_CODE"]
      
      payload["OrganizationId"] = transunion_property_id_code
      payload = json.dumps(payload)

      auth_encryption = create_auth_encryption(payload, auth_response["Nonce"], auth_response["Timestamp"], transunion_property_id_code, parameter_store["TRANSUNION_SECRET_KEY"])
      headers_auth = f'{constants["RESIDENT_ID"]}{transunion_property_id_code}:{auth_encryption}:{auth_response["Timestamp"]}:{auth_response["Nonce"]}'
      # creates the required headers for the request
      headers = {
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
        "Access-Control-Allow-Methods": "POST, HEAD, OPTIONS",
        "Access-Control-Allow-Origin": "*",
        "Content-type":"application/json", 
        "Accept":"application/json",
        "Authorization": headers_auth
      }
      
      # ------------- handles the TransUnion requests ------------- #
      identity_response = requests.post(identity_url, data=payload, headers=headers)
      
      # succesful request
      if identity_response.status_code == constants["HTTP_GOOD_RESPONSE_CODE"]:
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
    except Exception:
        # in case an error ocurred while doing the requests
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
  

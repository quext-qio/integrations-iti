import os
import json
import requests
import time

from Utils.Converter import Converter
from Utils.Constants import constants

def lambda_handler(event, context):
    parameter_store = json.loads(os.environ.get("parameter_store"))

    payload = event["body"]
    leasing_host = parameter_store["LEASING_HOST"]
    leasing_background_screening_endpoint = parameter_store["LEASING_BACKGROUND_SCREENING_ENDPOINT"]

    # convert xml to dict
    convert = Converter(payload)
    dict_response = convert.xml_to_dict(convert.data)

    # creates the applicants array
    applicants = []

    # populate the applicants array with the payload data
    for applicant in dict_response["gateway"]["application"]["applicants"]["applicant"]:
        caution_notes = applicant["scoreResult"]["cautionNotes"] if "cautionNotes" in applicant["scoreResult"] else {}
        notes = []

        # creates an array with the cautions notes 
        for key, value in caution_notes.items():
            notes.append(value)

        new_applicant = {
            "name": f"{applicant['firstName']} {applicant['lastName']}",
            "application_type": applicant["applicantType"],
            "criminal_recommendation_message": applicant["criminalRecommendation"],
            "eviction_recommendation_message": applicant["evictionRecommendation"],
            "applicant_score": applicant["scoreResult"]["applicantScore"] if "applicantScore" in applicant["scoreResult"] else None,
            "warning": applicant["scoreResult"]["warnings"] if "warnings" in applicant["scoreResult"] else {},
            "note": notes
        }

        applicants.append(new_applicant)
    
    # gets the application number 
    application_number = dict_response["gateway"]["application"]["applicationNumber"]
    household_id = ""

    try:
        success = False
        iterations = 0

        while success == False:
            response = requests.get(f"{parameter_store['LEASING_HOST']}/{application_number}")
            household_id = response.text
            iterations += 1

            if response.status_code == constants["HTTP_GOOD_RESPONSE_CODE"] or iterations == constants["BACKGROUND_SCREENING_MAX_ITERATIONS"]:
                success = True
            else:
                time.sleep(1)
        
        print(f"iterations done: {iterations} - for this application number: {application_number}")

        if response.status_code != constants["HTTP_GOOD_RESPONSE_CODE"]:
            temp_response = json.loads(household_id)
            print(f"The status response of the get household id (find-by-number) endpoint wasn't successful: {response.status_code}")

            return {
                "statusCode": response.status_code,
                "body": json.dumps({
                    "data": {},
                    "errors": temp_response["message"]
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",  
                },
                "isBase64Encoded": False  
            }
    except Exception as e:
      return {
            "statusCode": constants["HTTP_ERROR_CODE"],
            "body": json.dumps({
                "data": [],
                "errors": [{"message": f"{e}"}],
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  
            },
            "isBase64Encoded": False  
        }

    # creates the headers & payload for the background screening update
    score_result = dict_response["gateway"]["scoreResult"]
    headers = {
        "Content-Type": "application/json"
    }
    body = {
        "applicants": applicants,
        "application_score": score_result["applicationScore"] if "applicationScore" in score_result else None,
        "household_id": household_id,
        "recommendation_message": score_result["recommendationMessage"],
        "policy_message": score_result["policyMessage"] if "policyMessage" in score_result else "",
        "application_recommendation_message": score_result["applicationRecommendationMessage"],
        "application_recommendation_description": score_result["applicationRecommendationDescription"],
        "transunion_application_number": application_number
    }

    # create the url needed for the leasing endpoint 
    url = f"{leasing_host}{leasing_background_screening_endpoint}{household_id}"

    # call to update the data
    try:
        leasing_response = requests.patch(url, data=json.dumps(body), headers=headers)

        if leasing_response.status_code == constants["HTTP_GOOD_RESPONSE_CODE"]:
            return {
                "statusCode": constants["HTTP_GOOD_RESPONSE_CODE"],
                "body": json.dumps({
                    "data": json.loads(leasing_response.text),
                    "errors": []
                }),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",  
                },
                "isBase64Encoded": False  
            }
        else:
          # if Leasing/requests returns an error
          return {
              "statusCode": leasing_response.status_code,
              "body": json.dumps({
                  "data": [],
                  "errors": json.loads(leasing_response.text)
              }),
              "headers": {
                  "Content-Type": "application/json",
                  "Access-Control-Allow-Origin": "*",  
              },
              "isBase64Encoded": False  
          }
    except Exception as e:
        # in case an error ocurred while doing the requests
        return {
            "statusCode": constants["HTTP_ERROR_CODE"],
            "body": json.dumps({
                "data": [],
                "errors": [{"message": f"{e}"}],
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",  
            },
            "isBase64Encoded": False  
        }
import json
import os
import requests
from constants.Constants import *
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) One Time Link Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    # Extract the 'fragment' parameter from the API Gateway event
    fragment = ""
    if event[QUERY_STRING_PARAM] and FRAGMENT in event[QUERY_STRING_PARAM]:
        fragment = event[QUERY_STRING_PARAM][FRAGMENT]
        logger.info(f"Fragment value in query string: {fragment}")
    else:
        # Case: Missing query string parameter
        logger.warning(f"Fragment value in query string is missing")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': "Fragment value in query string is missing"})
        }

    # Define the URL of the external service
    base_url = os.environ[HOST]
    endpoint = PATH.format(fragment=fragment)
    url = f"{base_url}{endpoint}"

    headers = {
        'Accept': event['headers']['Accept'],
        'Content-Type': 'application/json'
    }

    try:
        # Make an HTTP GET request to the external service
        logger.info(f"Calling external service with URL: {url}")
        response = requests.get(url, headers=headers)
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response data: {response.text}")
        response_data = {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': response.headers.get('Content-Type', 'application/json')
            },
            'body': response.text
        }
    except Exception as e:
        # Handle any exceptions that may occur during the request
        logger.error(f"Exception occurred calling external service {url}: {e}")
        response_data = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }

    return response_data

import json, os
import requests
from constants.Constants import *

def lambda_handler(event, context):
    # Extract the 'fragment' parameter from the API Gateway event
    fragment = ""
    if event[QUERY_STRING_PARAM] and  FRAGMENT in event[QUERY_STRING_PARAM]:
    
        fragment = event[QUERY_STRING_PARAM][FRAGMENT]
    else:
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
        response = requests.get(url, headers=headers)
        response_data = {
            'statusCode': response.status_code,
            'headers': {
                'Content-Type': response.headers.get('Content-Type', 'application/json')
            },
            'body': response.text
        }
    except Exception as e:
        # Handle any exceptions that may occur during the request
        response_data = {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': str(e)})
        }
    
    return response_data

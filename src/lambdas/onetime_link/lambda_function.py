import json, os
import requests
from constants.Constants import *

def lambda_handler(event, context):
    # Extract the 'fragment' parameter from the API Gateway event
    if QUERY_STRING_PARAM not in event:
        return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': "No query Parameters in event"})
            }
    
    if FRAGMENT not in event[QUERY_STRING_PARAM]:
        return  {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': "No fragment value in query Parameters"})
            }
    
    fragment = event[QUERY_STRING_PARAM][FRAGMENT]
    
    # Define the URL of the external service
    base_url = os.environ[HOST]
    endpoint = PATH.format(fragment=fragment)
    url = f"{base_url}{endpoint}"
    
    # Define headers if needed
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

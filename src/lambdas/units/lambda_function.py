import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory
from datetime import date

def lambda_handler(event, context):
    headers = event['headers']
    print(headers)
    wsgi_input = {
        'PATH_INFO': event['resource'],
        'REQUEST_METHOD': "POST",
        'HTTP_X_API_KEY': headers['x-api-key']
    }
    
    input_data = json.loads(event['body'])
    # Obtain the result from DataControllerFactory().create_data_controller(input_data, event)
    code, result= DataControllerFactory().create_data_controller(input_data, wsgi_input)
    print(result)

    # Convert date objects to strings
    result = convert_dates_to_strings(result)

    return {
        'statusCode': code,
        'body': json.dumps(result),  # Convert the result to JSON
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

def convert_dates_to_strings(data):
    if isinstance(data, dict):
        return {key: convert_dates_to_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_dates_to_strings(item) for item in data]
    elif isinstance(data, date):
        return data.isoformat()
    else:
        return data

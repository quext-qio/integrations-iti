import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory
from datetime import date

def lambda_handler(event, context):
    # headers = event['headers']
    # wsgi_input = {
    #     'PATH_INFO': '/api/v1/leases',
    #     'REQUEST_METHOD': "POST"
    # }
    # if 'x-api-key' in headers:
    #     wsgi_input['HTTP_X_API_KEY'] = headers['x-api-key']

    input = json.loads(event['body'])
    code, response = DataControllerFactory().create_data_controller(input)
    # Convert date objects to strings
    result = convert_dates_to_strings(response)

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

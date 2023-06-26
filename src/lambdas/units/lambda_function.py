import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory
from datetime import date

def lambda_handler(event, context):
    input_data = json.loads(event['body'])
    # Obtain the result from DataControllerFactory().create_data_controller(input_data, event)
    result = DataControllerFactory().create_data_controller(input_data)

    # Convert date objects to strings
    result = convert_dates_to_strings(result)

    return {
        'statusCode': "200",
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

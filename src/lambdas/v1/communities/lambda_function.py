import json
from DataPushPullShared.DataController import DataController
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) General Communities Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    headers = event['headers']
    wsgi_input = {
        'PATH_INFO': event['resource'],
        'REQUEST_METHOD': "POST"
    }
    if 'x-api-key' in headers:
        wsgi_input['HTTP_X_API_KEY'] = headers['x-api-key']

    input = json.loads(event['body'])
    code, data_controller = DataController("info").get_communities(
        input.get("customerUUID", ""), wsgi_input)
    return {
        'statusCode': code,
        'body':  json.dumps(data_controller),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

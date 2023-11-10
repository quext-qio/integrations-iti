import json
from DataController.DataControllerFactory import DataControllerFactory
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Tour Availability Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    input = json.loads(event['body'])
    code, data = DataControllerFactory().create_data_controller(input, logger)
    logger.info(f"Response from DataController: code = {code}, data = {data}")
    return {
        'statusCode': code,
        'body': json.dumps(data),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

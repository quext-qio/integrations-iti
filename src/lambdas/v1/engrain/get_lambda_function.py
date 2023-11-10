import json
from config.engrain_job_status import EngrainJob
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Engrain Job Status Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    engrain_info = EngrainJob()
    logger.info(f"Job status: {engrain_info.get_status()}")
    return {
        'statusCode': "200",
        'body': json.dumps({
            'data': engrain_info.get_status(),
            'errors': {},
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

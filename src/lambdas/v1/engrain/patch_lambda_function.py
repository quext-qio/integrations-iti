import json
from config.engrain_job_status import EngrainJob
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Engrain Job Update Lambda")


def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    input = json.loads(event['body'])

    if "run" not in input:
        logger.warning(f"Bad Request: run is required: {input}")
        return {
            'statusCode': "400",
            'body': json.dumps({
                'data': {},
                'errors': "run is required",
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False
        }

    # Check the status of the job
    engrain_info = EngrainJob()
    if f"{input['run']}" == "True":
        engrain_info.start()
        logger.info(f"Job allowed to start")
    else:
        engrain_info.stop()
        logger.info(f"Job allowed to stop")

    is_running = engrain_info.is_running()
    logger.info(f"Job status: {is_running}")
    return {
        'statusCode': "200",
        'body': json.dumps({
            'data': {
                "job_enabled": f"{is_running}",
            },
            'errors': {},
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

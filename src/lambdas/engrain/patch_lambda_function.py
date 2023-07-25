import json
from config.engrain_job_status import EngrainJob

def lambda_handler(event, context):
    input = json.loads(event['body'])

    if "run" not in input:
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
    else:
        engrain_info.stop()

    is_running = engrain_info.is_running()
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
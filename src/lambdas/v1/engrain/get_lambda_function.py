import json
from config.engrain_job_status import EngrainJob

def lambda_handler(event, context):
    engrain_info = EngrainJob()
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
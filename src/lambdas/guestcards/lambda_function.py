import json

def lambda_handler(event, context):
    input = json.loads(event['body'])
    return {
        'statusCode': "201",
        'body': json.dumps({
            'data': 'Hello from Guestcards',
            'errors': []
        }),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  
        },
        'isBase64Encoded': False  
    }
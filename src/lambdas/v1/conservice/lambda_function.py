import json

def lambda_handler(event, context):
    input = json.loads(event['body'])
    
    return {
        "statusCode": "200",
        "body": json.dumps({
            "data": f"hello from conservice {input}",
            "errors": []
        }),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  
        },
        "isBase64Encoded": False  
    }

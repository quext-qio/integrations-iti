import json

def lambda_handler(event, context):
    path_parameters = event.get('pathParameters', {})
    customerUUID = path_parameters.get('customerUUID', None)
    action = path_parameters.get('action', None)
    communityUUID = path_parameters.get('communityUUID', None)
    return {
        "statusCode": "200",
        "body": json.dumps({
            "data": f"hello from rentdynamics {customerUUID}, {action}, {communityUUID}",
            "errors": []
        }),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",  
        },
        "isBase64Encoded": False  
    }

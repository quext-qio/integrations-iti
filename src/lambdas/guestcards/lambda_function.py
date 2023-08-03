import json
from factory.service_factory import ServiceFactory

def lambda_handler(event, context):
    input = json.loads(event['body'])
    # #TODO: Get service type from IPS and validate names
    # service_type_name = "Resman"
    # service = ServiceFactory.get_service(service_type_name)
    # return service.get_data(input)




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
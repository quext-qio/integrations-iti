import json
from DataPushPullShared.DataControllerFactory import DataControllerFactory

def lambda_handler(event, context):
    input = json.loads(event['body'])
    print(event)

    # Obtener el resultado de DataControllerFactory().create_data_controller(input, event)
    #result = DataControllerFactory().create_data_controller(input, event)

    return {
        'statusCode': "200",
        'body': {"hi":"hi"},  # Convertir el resultado a JSON
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False
    }

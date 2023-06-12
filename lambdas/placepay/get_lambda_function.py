import place
from Schemas.SchemaRequestPost import SchemaRequestPost
from Config.Config import config

def lambda_handler(event, context):
    # return {
    #     'statusCode': 400,
    #     'data': ["Sucess"],
    #     'errors': []
    # }

    response = {
        'statusCode': "400",
        'body': 'Mensaje de error o información adicional',
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'isBase64Encoded': False  
    }
    return response
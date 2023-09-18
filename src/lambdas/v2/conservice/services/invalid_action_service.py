import json
from abstract.service_interface import ServiceInterface

class InvalidActionService(ServiceInterface):
    def get_data(self, body: dict):
        return {
            'statusCode': "400",
            'body': json.dumps({
                'data': {},
                'errors': [
                    {
                        'message': 'Invalid Parameter value'
                    }
                ]
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
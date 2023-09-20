import json
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class InvalidActionService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        return {
            'statusCode': Constants.HTTP_BAD_RESPONSE_CODE,
            'body': json.dumps({
                'data': {},
                'errors': [
                    {
                        'message': 'Invalid action'
                    }
                ]
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
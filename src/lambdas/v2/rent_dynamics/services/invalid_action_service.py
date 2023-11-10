import json
from abstract.service_interface import ServiceInterface

class InvalidActionService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict, logger):
        logger.info(f"Bad request: Invalid action")
        return {
            'statusCode': "400",
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
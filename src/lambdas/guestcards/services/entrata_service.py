import json
from abstract.service_interface import ServiceInterface

class EntrataService(ServiceInterface):
    def get_data(self, body):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from Entrata',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
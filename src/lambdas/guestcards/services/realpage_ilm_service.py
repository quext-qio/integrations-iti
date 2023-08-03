import json
from abstract.service_interface import ServiceInterface

class RealPageILMService(ServiceInterface):
    def get_data(self, body):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from Real Page ILM',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
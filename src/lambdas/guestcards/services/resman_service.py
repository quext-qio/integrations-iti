import json
from abstract.service_interface import ServiceInterface

class ResManService(ServiceInterface):
    def get_data(self, body: dict, ips_response: dict):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from ResMan',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
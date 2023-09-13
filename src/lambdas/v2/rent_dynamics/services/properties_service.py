import json
from abstract.service_interface import ServiceInterface

class PropertiesService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from PropertiesService',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
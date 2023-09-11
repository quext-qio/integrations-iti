import json
from abstract.service_interface import ServiceInterface

class CustomerEventsService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from CustomerEventsService',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
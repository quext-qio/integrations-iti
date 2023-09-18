import json
from abstract.service_interface import ServiceInterface

class TenantsService(ServiceInterface):
    def get_data(self,body: dict):
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from TenantsService',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
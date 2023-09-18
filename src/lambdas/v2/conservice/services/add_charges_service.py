import json
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper

class AddChargesService(ServiceInterface):
    def get_data(self, body: dict):

        # Success response
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': "AddChargesService",
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
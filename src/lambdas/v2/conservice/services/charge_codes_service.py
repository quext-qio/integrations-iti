import json
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class ChargeCodesService(ServiceInterface):
    def get_data(self, body: dict):
       
        # Success response
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': "ChargeCodesService",
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
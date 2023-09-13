import json
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class ChargeCodesService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        params = {
            'community_id': body['community_id']
        }

        # Get data from database
        is_success, data = NewCoMapper.get_chargeCodes_RentDynamics(params=params)
        if not is_success:
            return {
                'statusCode': "500",
                'body': json.dumps({
                    'data': {},
                    'errors': data
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }


        # Success response
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': data,
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
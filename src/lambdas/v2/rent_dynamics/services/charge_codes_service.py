import json
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class ChargeCodesService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        # Get path parameters
        # customerUUID = path_parameters['customerUUID']
        # action = path_parameters['action']
        # communityUUID = path_parameters['communityUUID']

        # Get body parameters
        # move_in_date = body['move_in_date']
        # move_out_date = body['move_out_date']
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


        # Suceess response
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
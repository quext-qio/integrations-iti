import json
from abstract.service_interface import ServiceInterface

class ChargeCodesService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):
        # # Get path parameters
        # customerUUID = path_parameters['customerUUID']
        # action = path_parameters['action']
        # communityUUID = path_parameters['communityUUID']

        # # Get body parameters
        # move_in_date = body['move_in_date']
        # move_out_date = body['move_out_date']

        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': 'data from ChargeCodesService',
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
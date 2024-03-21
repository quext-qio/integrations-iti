import json

from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class ProspectService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict, logger) -> any:
        params = {'community_id': body['community_id'],
                  'create_date': body['create_date']}
        is_success, data = NewCoMapper.get_prospect_rent_dynamics(params)
        if not is_success:
            # Case: Error getting data from database
            logger.error(f"Error occurred in database for prospects")
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
        logger.info(f"Successfully retrieved prospects from database")
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

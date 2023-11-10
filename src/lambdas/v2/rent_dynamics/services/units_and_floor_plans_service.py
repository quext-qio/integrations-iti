import json
from abstract.service_interface import ServiceInterface
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class UnitsAndFloorPlantsService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict, logger):
        # Get body parameters
        community_id = body['community_id']

        # Create params required for the query
        params = {
            'community_id': community_id,
        }

        # Get data from database
        logger.info(f"Getting units and floor plans from database")
        is_success, data = NewCoMapper.get_units_and_floorplans_RentDynamics(
            params=params)
        if not is_success:
            # Case: Error getting data from database
            logger.error(f"Error getting units and floor plans from database")
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
        logger.info(
            f"Successfully retrieved units and floor plans from database")
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

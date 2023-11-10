import json
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class ResidentsService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict, logger):

        if 'move_in_date' not in body and 'move_out_date' not in body:
            # Bad Request: move_in_date and move_out_date are required for this action
            logger.info(
                f"Bad request: move_in_date and move_out_date are required for this action")
            return {
                'statusCode': "400",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": 'move_out_date and move_in_date are required for this action'}]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        # Get body parameters
        move_in_date = body['move_in_date']
        move_out_date = body['move_out_date']
        community_id = body['community_id']

        # Validate the dates
        move_in_date_obj = datetime.strptime(move_in_date, '%Y-%m-%d')
        move_out_date_obj = datetime.strptime(move_out_date, '%Y-%m-%d')
        if move_out_date_obj <= move_in_date_obj:
            # Bad Request: move_out_date is less than or equal to move_in_date
            logger.info(
                f"Bad request: move_out_date must be greater than move_in_date")
            return {
                'statusCode': "400",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": 'move_out_date must be greater than move_in_date'}]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        # Create params required for the query
        params = {
            'community_id': community_id,
            'move_in_date': move_in_date,
            'move_out_date': move_out_date,
        }

        # Get data from database
        logger.info(f"Getting residents from database")
        is_success, data = NewCoMapper.get_residents_RentDynamics(
            params=params)
        if not is_success:
            # Case: Error getting data from database
            logger.error(f"Error getting residents from database")
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
        logger.info(f"Successfully retrieved residents from database")
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

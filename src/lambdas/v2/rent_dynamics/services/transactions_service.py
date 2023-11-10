import json
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper


class TransactionsService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict, logger):

        if 'start_date' not in body and 'end_date' not in body and 'resident_id' not in body:
            # Bad request: start_date, end_date and resident_id are required for this action
            logger.info(
                f"Bad request: start_date, end_date and resident_id are required for this action")
            return {
                'statusCode': "400",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": 'start_date, end_date and resident_id are required for this action'}]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        # Get body parameters
        start_date = body['start_date']
        end_date = body['end_date']
        resident_id = body['resident_id']
        community_id = body['community_id']

        # Validate the dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date_obj <= start_date_obj:
            # Bad Request: end_date is less than or equal to start_date
            logger.info(
                f"Bad request: end_date must be greater than start_date")
            return {
                'statusCode': "400",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": 'end_date must be greater than start_date'}]
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
            'resident_id': resident_id,
            'start_date': start_date,
            'end_date': end_date,
        }

        # Get data from database
        logger.info(f"Getting transactions from database")
        is_success, data = NewCoMapper.get_transactions_RentDynamics(
            params=params)
        if not is_success:
            # Case: Error getting data from database
            logger.error(f"Error getting transactions from database")
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
        logger.info(f"Successfully retrieved transactions from database")
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

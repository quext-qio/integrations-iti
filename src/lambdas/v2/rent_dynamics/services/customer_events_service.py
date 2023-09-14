import json
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper

class CustomerEventsService(ServiceInterface):
    def get_data(self, path_parameters: dict, body: dict):

        # Get body parameters
        start_date = body['start_date']
        end_date = body['end_date']
        community_id = body['community_id']

        # Validate the dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        if end_date_obj <= start_date_obj:
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
            'start_date': start_date,
            'end_date': end_date,
        }

        # Get data from database
        is_success, data = NewCoMapper.get_customer_events_RentDynamics(params=params)
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
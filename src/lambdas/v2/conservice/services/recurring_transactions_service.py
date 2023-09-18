import json
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.newco_mapper import NewCoMapper

class RecurringTransactionsService(ServiceInterface):
    def get_data(self, body: dict):
        return {
                    'statusCode': "200",
                    'body': json.dumps({
                        'data': 'data from RecurringTransactionsService',
                        'errors': []
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',  
                    },
                    'isBase64Encoded': False  
                }
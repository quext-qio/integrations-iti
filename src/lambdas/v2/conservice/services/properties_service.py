import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class PropertiesService(ServiceInterface):
    def get_data(self, body: dict):
        conservice_outgoing = Constants.HOST + Constants.PATH
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Call conservice outgoing
            response = requests.get(conservice_outgoing, headers=headers, params= body)
            response_data = {
                    "properties": [self.exclude_keys(item) for item in json.loads(response.text)[Constants.PROPERTIES]]
                }

       
            return {
                'statusCode': Constants.HTTP_GOOD_RESPONSE_CODE,
                'body': json.dumps({
                    'data': response_data,
                    'errors': {}
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }

        except Exception as e:
            return {
                'statusCode': Constants.HTTP_BAD_RESPONSE_CODE,
                'body': json.dumps({
                    'data': {},
                    'errors': [
                        {
                            'message': f'Error trying to call Conservice endpoint: {e}'
                        }
                    ]
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }
    

                
    def exclude_keys(self, d, keys=[Constants.METHODS]):
        """
        Remove the method keys from the input payload 
        and return the dict
        """
        return {x: d[x] for x in d if x not in keys}
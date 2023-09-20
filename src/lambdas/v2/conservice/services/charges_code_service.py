import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class ChargesCodeService(ServiceInterface):
    def get_data(self, body: dict):
        parameter = body[Constants.PARAMETER]
        conservice_outgoing = f'{Constants.HOST}{Constants.PATH}/{parameter}'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Call conservice outgoing
            response = requests.get(conservice_outgoing, headers=headers, params= body)
            response_data = json.loads(response.text)

       
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
    

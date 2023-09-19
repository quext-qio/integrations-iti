import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class ChargesCodeService(ServiceInterface):
    def get_data(self, body: dict):
        parameter = body['Parameter']
        conservice_outgoing = f'{Constants.HOST}{Constants.PATH}/{parameter}'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Call conservice outgoing
            response = requests.get(conservice_outgoing, headers=headers, params= body)
            response_data = json.loads(response.text)

       
            return {
                'statusCode': "200",
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
                'statusCode': "400",
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
    

import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class AddChargesService(ServiceInterface):
    def get_data(self, body: dict):
        parameter = body['Parameter']
        conservice_outgoing = f'{Constants.HOST}{Constants.PATH}/{parameter}'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            if isinstance(body['charges'], list):
            # If 'charges' is a list, iterate over its elements and replace single quotes
                for i in range(len(body['charges'])):
                    if isinstance(body['charges'][i], str):
                        body['charges'][i] = body['charges'][i].replace("'", '"')
            elif isinstance(body['charges'], str):
                # If 'charges' is a string, replace single quotes within it
                body['charges'] = body['charges'].replace("'", '"')

            # Call conservice outgoing
            charges = {
                "charges": body['charges']
            }
            response = requests.post(conservice_outgoing, headers=headers, data= json.dumps(charges))
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
    

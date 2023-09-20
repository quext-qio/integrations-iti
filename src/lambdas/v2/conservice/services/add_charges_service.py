import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants

class AddChargesService(ServiceInterface):
    def get_data(self, body: dict):
        parameter = body[Constants.PARAMETER]
        conservice_outgoing = f'{Constants.HOST}{Constants.PATH}/{parameter}'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            if isinstance(body[Constants.CHARGES], list):
            # If 'charges' is a list, iterate over its elements and replace single quotes
                for i in range(len(body[Constants.CHARGES])):
                    if isinstance(body[Constants.CHARGES][i], str):
                        body[Constants.CHARGES][i] = body[Constants.CHARGES][i].replace("'", '"')
            elif isinstance(body[Constants.CHARGES], str):
                # If 'charges' is a string, replace single quotes within it
                body[Constants.CHARGES] = body[Constants.CHARGES].replace("'", '"')

            # Call conservice outgoing
            charges = {
                "charges": body[Constants.CHARGES]
            }
            response = requests.post(conservice_outgoing, headers=headers, data= json.dumps(charges))
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
    

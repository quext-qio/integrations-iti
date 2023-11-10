import json
import requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants


class ChargesCodeService(ServiceInterface):
    def get_data(self, body: dict, logger):
        parameter = body[Constants.PARAMETER]
        conservice_outgoing = f'{Constants.HOST}{Constants.PATH}/{parameter}'
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Call conservice outgoing
            logger.info(
                f'Calling Conservice endpoint {conservice_outgoing} with payload: {body} to get charges code')
            response = requests.get(
                conservice_outgoing,
                headers=headers,
                params=body
            )
            logger.info(
                f'Conservice response status code: {response.status_code}')
            response_data = json.loads(response.text)
            logger.info(f'Conservice response data: {response_data}')

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
            logger.error(
                f'Error trying to call Conservice endpoint {conservice_outgoing}: {e}')
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

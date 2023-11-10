import json
import requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants


class PropertiesService(ServiceInterface):
    def get_data(self, body: dict, logger):
        conservice_outgoing = Constants.HOST + Constants.PATH
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Call conservice outgoing
            logger.info(
                f'Calling Conservice endpoint {conservice_outgoing} with payload: {body} to get properties')
            response = requests.get(
                conservice_outgoing,
                headers=headers,
                params=body
            )
            logger.info(
                f'Conservice response status code: {response.status_code}')
            response_data = {
                "properties": [self.exclude_keys(item) for item in json.loads(response.text)[Constants.PROPERTIES]]
            }
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
                f"Error trying to call Conservice endpoint {conservice_outgoing}: {e}")
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

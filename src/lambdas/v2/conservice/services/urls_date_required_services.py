import json
import requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants
from datetime import datetime
from dateutil.relativedelta import relativedelta


class URLDateRequiredServices(ServiceInterface):
    def get_data(self, body: dict, logger):
        parameter = body[Constants.PARAMETER]
        conservice_outgoing = f"{Constants.HOST}{Constants.PATH}/{parameter}"
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            # Calculate the start_date as no more than 3 months ago
            if Constants.START_DATE in body:
                start_date = body[Constants.START_DATE] if body[Constants.START_DATE] else self.calculate_start_date(
                )
                body[Constants.START_DATE] = start_date

            # Call conservice outgoing
            logger.info(
                f'Calling Conservice endpoint {conservice_outgoing} with payload: {body} to get URL date required')
            response = requests.get(
                conservice_outgoing,
                headers=headers,
                params=body
            )
            logger.info(
                f"Conservice response status code: {response.status_code}")

            if response.status_code == Constants.HTTP_GOOD_RESPONSE_CODE:
                data = json.loads(response.text)
                tenants = parameter == Constants.TENANTS
                filtered_data = self.filter_current_residents(data, tenants)

                # Replace the array data with the filtered results
                if tenants:
                    data[Constants.LEASES] = filtered_data
                else:
                    data[Constants.CHARGES] = filtered_data

                logger.info(f'Success conservice response data: {data}')
                return {
                    'statusCode': Constants.HTTP_GOOD_RESPONSE_CODE,
                    'body': json.dumps({
                        'data': data,
                        'errors': {}
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'isBase64Encoded': False
                }

            else:
                logger.error(
                    f'Error from Conservice endpoint, status code not 200: {response.status_code}')
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps({
                        'data': {},
                        'errors': [
                            {
                                'message': f'Error from Conservice endpoint'
                            }
                        ]
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

    def calculate_start_date(self):
        # Calculate the start_date as no more than 3 months ago
        temp_date = datetime.today().replace(day=1)
        start_date = (temp_date - relativedelta(months=2)).strftime("%Y-%m-%d")
        return start_date

    def filter_current_residents(self, data, tenants):
        residents_key = Constants.LEASES if tenants else Constants.CHARGES
        filtered_residents = [resident for resident in data[residents_key]
                              if resident[Constants.RESIDENT_STATUS] == Constants.CURRENT]
        return filtered_residents

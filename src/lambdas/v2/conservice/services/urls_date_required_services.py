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
            if Constants.START_DATE in body and Constants.END_DATE in body:
                if not self.validate_duration(body[Constants.START_DATE], body[Constants.END_DATE]):
                    return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'data': {},
                        'errors': [
                            {
                                'message': f'The duration between start & end dates cannot be more than 2 months'
                            }
                        ]
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'isBase64Encoded': False
                }
            else:
                body[Constants.START_DATE] = self.calculate_start_date()
                body[Constants.END_DATE] = datetime.today().strftime("%Y-%m-%d")

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
    
    def validate_duration(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Calculate the difference in months
        duration_in_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

        # Check if the duration is less than three months
        if abs(duration_in_months) < 3:
            return True
        else:
            return False

    def filter_current_residents(self, data, tenants):
        residents_key = Constants.LEASES if tenants else Constants.CHARGES
        filtered_residents = [resident for resident in data[residents_key]
                              if resident[Constants.RESIDENT_STATUS] == Constants.CURRENT]
        return filtered_residents

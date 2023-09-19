import json, requests
from abstract.service_interface import ServiceInterface
from constants.constants import Constants
from datetime import datetime
from dateutil.relativedelta import relativedelta

class URLDateRequiredServices(ServiceInterface):
    def get_data(self, body: dict):
        parameter = body['Parameter']
        conservice_outgoing = f"{Constants.HOST}{Constants.PATH}/{parameter}"
        headers = {
            'Content-Type': 'application/json'
        }

        try:
            start_date = body["start_date"] if body["start_date"] else self.calculate_start_date()
            body['start_date'] = start_date

            # Call conservice outgoing
            response = requests.get(conservice_outgoing, headers=headers, params= body)

                # Calculate the start_date as no more than 3 months ago
            if response.status_code == Constants.HTTP_GOOD_RESPONSE_CODE:
                data = json.loads(response.text)
                tenants = parameter == "tenants"
                filtered_data = self.filter_current_residents(data, tenants)
                
                # Replace the array data with the filtered results
                if tenants:
                    data["leases"] = filtered_data
                else:
                    data["charges"] = filtered_data

                return {
                    'statusCode': "200",
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
    

    def calculate_start_date(self):
        # Calculate the start_date as no more than 3 months ago
        temp_date = datetime.today().replace(day=1)
        start_date = (temp_date - relativedelta(months=2)).strftime("%Y-%m-%d")
        return start_date

    def filter_current_residents(self, data, tenants):
        residents_key = "leases" if tenants else "charges"
        filtered_residents = [resident for resident in data[residents_key] if resident['resident-status'] == 'current']
        return filtered_residents

  
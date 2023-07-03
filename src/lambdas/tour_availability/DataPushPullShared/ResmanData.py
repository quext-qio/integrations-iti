import requests, json
from Utils.Config.Config import config
from Utils.Constants.QuextConstants import QuextConstants

class DataResman:

    def get_tour_availability(self, ips, event):
        print("Resman")
        url = f'{config[QuextConstants.QUEX_HOST]}{QuextConstants.PATH}'
        body = event

        headers = {
            'Content-Type': 'application/json'
        }

        outgoing_quext_response = requests.post(url, headers=headers, json=body)
        print(outgoing_quext_response.text)
        print(type(outgoing_quext_response.text))
        return json.loads(outgoing_quext_response.text)[QuextConstants.AVAILABLE_TIMES], []
               
      
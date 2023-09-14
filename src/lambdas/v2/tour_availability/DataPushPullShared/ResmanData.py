import requests, json
from Utils.Config.Config import config
from Utils.Constants.QuextConstants import QuextConstants
import logging

class DataResman:

    def get_tour_availability(self, ips, event):
        url = f'{config[QuextConstants.QUEX_HOST]}{QuextConstants.PATH}'
        body = event

        headers = {
            'Content-Type': 'application/json'
        }
        try:
            outgoing_quext_response = requests.post(url, headers=headers, json=body)
            return json.loads(outgoing_quext_response.text)[QuextConstants.AVAILABLE_TIMES], []
        except Exception as e:
            logging.error(f"Error Quext endpoint: {e}")
            return [], f"Error from Quext: {e}"
            
                
      
import requests, json
from Utils.Config.Config import config

class DataResman:

    def get_tour_availability(self, ips, event):
        url = config["Quext_calendar_host"]
        body = event

        headers = {
            'Content-Type': 'application/json'
        }

        outgoing_quext_response = requests.post(url, headers=headers, json=body)

       
        return json.loads(outgoing_quext_response.text)["available_times"], []
               
      
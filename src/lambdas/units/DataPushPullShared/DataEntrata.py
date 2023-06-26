import json
import requests

class DataEntrata:

    def get_unit_availability(self):
        code = 200
        errors = []

        # These get replaced into the url template.
        _params = {"subdomain": "primeplacellc", "method": "properties"}

        _body = json.dumps({
            "auth": {"type": "basic"},
            "method": {"name": "getProperties", "params": {"showAllStatus": "1"}}
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic cXVleHRfYXBpQHByaW1lcGxhY2VsbGM6UXVleHQ2MTAyMDIyXg=='
        }

        url_template = 'https://{subdomain}.entrata.com/api/{method}'
        entrata_url = url_template.format(**_params)

        entrataChannelResponse = requests.post(entrata_url, data=_body, headers=headers)


        if entrataChannelResponse.status_code != 200:
            errors.append({ "status_code": entrataChannelResponse.status_code, 
                            "status": entrataChannelResponse.text.findall('Status')[0].text,
                            "message": entrataChannelResponse.text.findall('ErrorDescription')[0].text })
            return [], [], [], errors
        else:
            property, models, units = self.translateEntrataJSON(entrataChannelResponse.text, self)
            return property, models, units, []


    def translateEntrataJSON(self, entrataJSON ):

        property = 9
        models = 9        
        units = 9

        return property, models, units


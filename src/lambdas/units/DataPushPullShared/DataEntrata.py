import json


class DataEntrata:

    def get_unit_availability(self):
        code = 200
        errors = []

        # These get replaced into the url template.
        _params = { "subdomain": "primeplacellc",
                    "method": "properties",          
        }

        _body = json.dumps( { "auth": { "type": "basic" }, "method": { "name": "getProperties", "params": { "showAllStatus": "1" } } } )

        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic cXVleHRfYXBpQHByaW1lcGxhY2VsbGM6UXVleHQ2MTAyMDIyXg==' }

        entrataChannel = self.outgoing.plain_http['Entrata (External)']
        entrataChannelResponse = entrataChannel.conn.post(self.cid, _body, _params, headers=headers)

        self.logger.info(entrataChannelResponse.text)

        if entrataChannelResponse.status_code != 200:
            self.logger.info(entrataChannelResponse.status_code)
            errors.append({ "status_code": entrataChannelResponse.status_code, 
                            "status": entrataChannelResponse.text.findall('Status')[0].text,
                            "message": entrataChannelResponse.text.findall('ErrorDescription')[0].text })
            response = { "data": { "provenance": ["resman"] }, "errors": errors }
            code = 502
        else:
            property, models, units = self.translateEntrataJSON(entrataChannelResponse.text, self)
            response = { "data": { "provenance": ["entrata"], "property": property, "models": models, "units": units }, "errors": errors }


    def translateEntrataJSON(self, entrataJSON ):

        property = 9
        models = 9        
        units = 9

        return property, models, units


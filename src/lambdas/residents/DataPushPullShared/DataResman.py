
from urllib.parse import urlencode
import xml.etree.ElementTree as etree

class DataResman:
    def __init__(self, ips):
        self.ips = ips
        pass

    def get_resident_data(self, credentials):
        code = 200
        errors = []

        # These get replaced into the url template.
        _params = { "interface": "MITS",
                    "method": "GetMarketing4_0",          
        }
        # Actual payload.
        body = { "AccountID": credentials["body"]["AccountID"],
                 "IntegrationPartnerID": credentials["body"]["IntegrationPartnerID"],
                 "ApiKey": credentials["body"]["ApiKey"],
                 "PropertyID": self.ips["platformData"]["foreign_community_id"]
        }
        _body = urlencode(body, {"Content-type": "application/x-www-form-urlencoded"})

        # Headers. Probably doesn't need Accept, but blows up without Content-Length for sure.
        headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json', 'Content-Length': str(len(str(_body)))}

        resmanChannel = self.outgoing.plain_http['ResMan (External)']
        resmanChannelResponse = resmanChannel.conn.post(self.cid, _body, _params, headers=headers)

        xml = etree.fromstring(resmanChannelResponse.text)

        if resmanChannelResponse.status_code != 200:
            self.logger.info(resmanChannelResponse.status_code)
            errors.append({ "status_code": resmanChannelResponse.status_code, 
                            "status": xml.findall('Status')[0].text, 
                            "message": xml.findall('ErrorDescription')[0].text })
            response = { "data": { "provenance": ["resman"] }, "errors": errors }
            code = 502
        else:
            property, models, units = self.translateResmanXML(self, xml, "Leasing/GetCurrentResidents")
            response = { "data": { "provenance": ["resman"], "property": property, "models": models, "units": units }, "errors": errors }

        return response, code
    
    def translateResmanXML(self, xml, method):
        # This isn't true Xpath 1.0, but some subset with changes. See:
        # https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support

        if method == "MITS/GetMarketing4_0":
            xpath_prefix = "Response/PhysicalProperty/Property/PropertyID/"


        return property, models, units

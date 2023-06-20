from .DataController import DataController as Controller
from .DataNewco import DataNewco
from .DataQuext import DataQuext
from .DataResman import DataResman
from Utils.IPSController import IPSController
from Utils.AccessControl import AccessUtils as AccessControl

import json

class DataControllerFactory:

    def create_data_controller(self, input, event):
        code, ips_response =  IPSController().get_partner(input["communityUUID"],input["customerUUID"],"residents")
        ips_response = json.loads(ips_response.text)
        partner = ""
       
        if "platformData" in ips_response and "platform" in ips_response["platformData"]:
            partner = ips_response["platformData"]["platform"]
        else:
             return  json.dumps( { "errors": [ { "message": ips_response } ] } )
             
         # Get credentials
        # credentials, status = AccessControl.externalCredentials(event, [] , partner)
        # if status != "good":
        #         response = { "data": { "provenance": [partner] }, "errors": status }
        #         return response, 500
        
        if partner == "Newco":
            response, code = DataNewco.get_unit_availability(ips_response)
            return Controller("NewCo", response, code).built_response()
        elif partner == "ResMan":
            response, code = self.dataFromResman(ips_response)
            return Controller("ResMan", response, code).built_response()
        elif partner == "Entrata":
            response, code = self.dataFromEntrata(ips_response)
        elif partner == "RealPage":
            response, code = self.dataFromRealPage(ips_response)
        elif partner == "Engrain":
            response, code = self.dataFromEngrain(ips_response)
        else:
            code = 400
            errors = "Unknown platform."
            response = { "data": {partner}, "errors": errors }
            self.logger.info("Unknown platform.")
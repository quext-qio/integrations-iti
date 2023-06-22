from .DataController import DataController as Controller
from .DataNewco import DataNewco
from .DataQuext import DataQuext
from .ResmanData import DataResman
from Utils.IPSController import IPSController
from Utils.AccessControl import AccessUtils as AccessControl

import json

class DataControllerFactory:

    def create_data_controller(self, input, event):
        code, ips_response =  IPSController().get_partner(input["communityUUID"],input["customerUUID"],"units")
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
            property_data, models_data, units_data, code = DataNewco.get_unit_availability(ips_response)
            return Controller("NewCo", response, code).built_response(property_data, models_data, units_data)    
        elif partner == "ResMan":
            property_data, models_data, units_data, code = DataResman.get_unit_availability(ips_response)
            return Controller("ResMan", code).built_response(property_data, models_data, units_data)    
        elif partner == "Entrata":
            response, code = None, 200
        elif partner == "RealPage":
            response, code =  None, 200
        elif partner == "Engrain":
            response, code =  None, 200
        else:
            code = 400
            errors = "Unknown platform."
            response = { "data": {partner}, "errors": errors }
            return response, code
from .DataController import DataController as Controller
from .DataNewco import DataNewco
from .DataEntrata import DataEntrata
from .DataEngrain import DataEngrain
from .DataRealpage import DataRealpage
from .ResmanData import DataResman
from Utils.IPSController import IPSController
from Utils.AccessControl import AccessUtils as AccessControl

import json

class DataControllerFactory:

    def create_data_controller(self, input):
        code, ips_response =  IPSController().get_partner(input["communityUUID"],input["customerUUID"],"units")
        ips_response = json.loads(ips_response.text)
        partner = ""
       
        if "platformData" in ips_response and "platform" in ips_response["platformData"]:
            partner = ips_response["platformData"]["platform"]
        else:
             return  500, { "errors": [ { "message": ips_response } ] }
             
         # Get credentials
        # credentials, status = AccessControl.externalCredentials(event, [] , partner)
        # if status != "good":
        #         response = { "data": { "provenance": [partner] }, "errors": status }
        #         return response, 500
        print(ips_response)
        if partner == "Newco":
            property_data, models_data, units_data, errors = DataNewco().get_unit_availability(ips_response, input)
            return Controller("NewCo", errors).built_response(property_data, models_data, units_data)    
        elif partner == "ResMan":
            property_data, models_data, units_data, errors = DataResman().get_unit_availability(ips_response, input)
            return Controller("ResMan", errors).built_response(property_data, models_data, units_data)    
        elif partner == "Entrata":
            property_data, models_data, units_data, errors = DataEntrata().get_unit_availability()
            return Controller("Entrata", errors).built_response(property_data, models_data, units_data)   
        elif partner == "RealPage":
            property_data, models_data, units_data, errors = DataRealpage().get_unit_availability(ips_response)
            return Controller("Realpage", errors).built_response(property_data, models_data, units_data)   
        elif partner == "Engrain":
            property_data, models_data, units_data, errors = DataEngrain().get_unit_availability(ips_response)
            return Controller("Engrain", errors).built_response(property_data, models_data, units_data)   
        else:
            code = 400
            errors = "Unknown platform."
            return  code, errors
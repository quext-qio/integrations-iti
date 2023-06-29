from .DataController import DataController as Controller
from ..DataPushPullShared.DataPushPullShared.DataFunnel import DataNewco
from ..DataPushPullShared.DataPushPullShared.DataEntrata import DataEntrata
from ..DataPushPullShared.DataPushPullShared.DataRealpage import DataRealpage
from ..DataPushPullShared.DataPushPullShared.ResmanData import DataResman
from Utils.IPSController import IPSController
from Utils.AccessControl import AccessUtils as AccessControl

import json

class DataControllerFactory:

    def create_data_controller(self, input):
        code, ips_response =  IPSController().get_partner(input["communityUUID"],input["customerUUID"],"tourAvailability")
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
        if partner == "Funnel":
            data, errors = DataNewco().get_unit_availability(ips_response, input)
            return Controller("Funnel", errors).built_response(data)    
        elif partner == "ResMan":
            data, errors = DataResman().get_unit_availability(ips_response, input)
            return Controller("ResMan", errors).built_response(data)    
        elif partner == "Entrata":
            data, errors = DataEntrata().get_unit_availability()
            return Controller("Entrata", errors).built_response(data)   
        elif partner == "RealPage":
            data, errors = DataRealpage().get_unit_availability(ips_response)
            return Controller("Realpage", errors).built_response(data)   
        else:
            code = 400
            errors = "Unknown platform."
            return  code, errors
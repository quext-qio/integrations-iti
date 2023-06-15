from DataController import DataController
from DataNewCo import DataNewco
from DataQuext import DataQuext
from DataResman import DataResman
from Utils.IPSController import IPSController

import json

class DataControllerFactory:

    def create_data_controller(self, input):
        ips_response =  IPSController().get_partner(input["communityUUID"],input["customerUUID"],"residents")
        ips_response = ips_response.text
        partner = ""
        if "platformData" in ips_response and "platform" in ips_response["platformData"]:
            partner = ips_response["platformData"]["platform"]
        else:
             return  json.dumps( { "errors": [ { "message": ips_response } ] } )
             
        
        if partner == "Newco":
            newco_data = DataNewco.create_newco_data()
            return DataController(newco_data)
        elif partner == "Resman":
            resman_data = DataResman()
            return DataController(resman_data)
        elif partner == "Quext":
            quext_data = DataQuext(ips_response).get_resident_data(None)
            return DataController(quext_data)
        else:
            raise ValueError("Invalid partner")
        return DataController()
from .DataController import DataController as Controller
from .DataNewCo import DataNewco
from .DataQuext import DataQuext
from .DataResman import DataResman
from IPSController import IPSController
from AccessControl import AccessUtils as AccessControl

import json

class DataControllerFactory:

    def create_data_controller(self, input):
        code, ips_response =  IPSController().get_platform_data(input["communityUUID"],input["customerUUID"],"residents")
        ips_response = json.loads(ips_response.text)
        partner = ""
       
        if "platformData" in ips_response and "platform" in ips_response["platformData"]:
            partner = ips_response["platformData"]["platform"]
        else:
             return  code, json.dumps( { "errors": [ { "message": ips_response } ] } )
             
         # Get credentials
        # res, res_code= AccessControl.check_access_control(wsgi_input)
        # if res_code != 200:
        #     return res_code, res
        
        if partner == "Newco":
            errors, newco_data = DataNewco().get_resident_data(ips_response, input)
            return Controller("NewCo", newco_data, errors).built_response()
        elif partner == "ResMan":
            errors, resman_response = DataResman().get_resident_data(ips_response, input, [])
            return Controller("Resman", resman_response, errors).built_response()
        elif partner == "Quext":
            errors, quext_data = DataQuext(ips_response).get_resident_data(None)
            return Controller("Quext", quext_data, [])
        else:
            return 402, {"errors":"Invalid partner"}
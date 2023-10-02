from DataController.DataController import DataController
from DataPushPullShared.DataFunnel import DataFunnel
from DataPushPullShared.DataEntrata import DataEntrata
from DataPushPullShared.DataRealpage import DataRealpage
from DataPushPullShared.ResmanData import DataResman
from IPSController import IPSController

import json

class DataControllerFactory:

    def create_data_controller(self, input):
        code, ips_response =  IPSController().get_platform_data(input["platformData"]["communityUUID"],input["platformData"]["customerUUID"],"tourAvailability")
        ips_response = json.loads(ips_response.text)
        partner = ""
       
        if "platformData" in ips_response and "platform" in ips_response["platformData"]:
            partner = ips_response["platformData"]["platform"]
        elif code != 200:
             return  code, { "errors": [ { "message": ips_response } ] }
             
      
        if partner == "Funnel":
            data, errors = DataFunnel().get_tour_availability(ips_response, input)
            return DataController(errors).built_response(data)    
        elif partner == "Entrata":
            data, errors = DataEntrata().get_tour_availability()
            return DataController(errors).built_response(data)   
        elif  "realpage" in partner.lower():
            data, errors = DataRealpage().get_tour_availability(ips_response, input)
            return DataController(errors).built_response(data)   
        else:
            data, errors = DataResman().get_tour_availability(ips_response, input)
            return DataController(errors).built_response(data)    

from DataController.DataController import DataController
from DataPushPullShared.DataFunnel import DataFunnel
from DataPushPullShared.DataEntrata import DataEntrata
from DataPushPullShared.DataRealpage import DataRealpage
from DataPushPullShared.ResmanData import DataResman
from schemas.SchemaRequest import SchemaRequest
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
        

        dict1 = input["timeData"]
        dict2 = input["platformData"]
        input_to_validate = self.merge(dict1, dict2)
        
        # If exist an error in user input
        is_valid, input_errors = SchemaRequest(input_to_validate).is_valid()
        if not is_valid:
            errors = {}
            for k, v in input_errors.items():
                errors[f"{k}"] = v[0]  
            return 400, {
                            "data": {},
                            "error": errors
                        }
                            
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


    def merge(self, dict1, dict2):
        """Method to merge 2 dictionaries

        Args:
            dict1 (dict): first dictionary
            dict2 (dict): second dictionary

        Returns:
            dict: retuns a dict with values of two dictionaries
        """
        res = {**dict1, **dict2}
        return res
     

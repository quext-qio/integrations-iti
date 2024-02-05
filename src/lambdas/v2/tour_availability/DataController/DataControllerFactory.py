from DataController.DataController import DataController
from DataPushPullShared.DataFunnel import DataFunnel
from DataPushPullShared.DataEntrata import DataEntrata
from DataPushPullShared.DataRealpage import DataRealpage
from DataPushPullShared.ResmanData import DataResman
from DataPushPullShared.DataSpherexx import DataSpherexx
from schemas.SchemaRequest import SchemaRequest
from IPSController import IpsV2Controller

import json


class DataControllerFactory:

    def create_data_controller(self, input, logger):
        community = input["platformData"]["communityUUID"]
        customer = input["platformData"]["customerUUID"]
        purpose = "tourAvailability"
        code, ips_response = IpsV2Controller().get_platform_data(community, purpose)
        ips_response = ips_response.json()
        partner = ""

        if "partner_name" in ips_response:
            partner = ips_response["partner_name"]
            logger.info(f"Partner returned from IPS: {partner}")
        elif code != 200:
            logger.error(
                f"IPS returned status code {code} with message {ips_response} for community {community}, customer {customer}, purpose {purpose}")
            return code, {"error": [{"message": ips_response}]}

        dict1 = input["timeData"]
        dict2 = input["platformData"]
        input_to_validate = self.merge(dict1, dict2)

        # If exist an error in user input
        is_valid, input_errors = SchemaRequest(input_to_validate).is_valid()
        if not is_valid:
            errors = {}
            for k, v in input_errors.items():
                errors[f"{k}"] = v[0]
            logger.warning(f"Bad Request: {errors.items()}")
            return 400, {
                "data": {},
                "error": errors
            }

        if partner == "Funnel":
            data, errors = DataFunnel().get_tour_availability(ips_response, input)
            logger.info(f"Data from Funnel: {data}, errors: {errors}")
            return DataController(errors).built_response(data)
        elif partner == "Entrata":
            data, errors = DataEntrata().get_tour_availability(ips_response, input)
            logger.info(f"Data from Entrata: {data}, errors: {errors}")
            return DataController(errors).built_response(data)
        elif partner == "Spherexx":
            data, errors = DataSpherexx().get_tour_availability(ips_response, input)
            logger.info(f"Data from Spherexx: {data}, errors: {errors}")
            return DataController(errors).built_response(data)
        elif "realpage" in partner.lower():
            data, errors = DataRealpage().get_tour_availability(ips_response, input)
            logger.info(f"Data from Realpage: {data}, errors: {errors}")
            return DataController(errors).built_response(data)
        else:
            data, errors = DataResman().get_tour_availability(ips_response, input)
            logger.info(f"Data from Resman: {data}, errors: {errors}")
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

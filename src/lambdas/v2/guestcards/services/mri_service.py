import json
import requests
import os
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
from constants.mri_constants import *

class MRIService(ServiceInterface):

    def get_data(self, body, ips, logger):
        logger.info(f"Getting data from MRI")

        transformed_body = self.transform_payload(body)
        
        
        pass


    def transform_payload(payload, ips):
        move_in_date = payload["guestPreference"]["moveInDate"]
        visit_date = ""
        if "tourScheduleData" in payload:
            visit_date = payload["tourScheduleData"]["start"][: payload["tourScheduleData"]["start"].index("T")]


        transformed_data = {
            "propertyId": ips["platformData"]["foreign_community_id"],
            "firstName": payload["guest"]["first_name"],
            "lastName": payload["guest"]["last_name"],
            "comment": payload["guestComment"],
            "emailAddress": payload["guest"]["email"],
            "type": "P",
            "cellPhoneNumber": payload["guest"]["phone"],
            "beds": len(payload["guestPreference"]["desiredBeds"]),
            "baths": payload["guestPreference"]["desiredBaths"][0], 
            "estimatedMoveInDate": move_in_date[ :move_in_date.index("T")],  # Extracting the date part
            "totalOccupants": payload["guestPreference"]["noOfOccupants"],
            "desiredLeaseTerm": payload["guestPreference"]["leaseTermMonths"],
            "visitDate": visit_date 
        }

        return transformed_data
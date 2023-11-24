import json
import requests
import os
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
from services.shared.quext_tour_service import QuextTourService
from constants.mri_constants import *

class MRIService(ServiceInterface):

    def get_data(self, body, ips, logger):
        logger.info(f"Getting data from MRI")

        transformed_body = self.transform_payload(body, ips)
        available_times = []
        tour_scheduled_id = ""
        tour_error = ""
        appointment_date = ""


        if "tourScheduleData" in body:
                appointment_date = body["tourScheduleData"]["start"]
                if appointment_date != "":
                    converted_date = datetime.strptime(appointment_date.replace(
                        "T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                    format_date = converted_date.strftime("%B %d, %Y")
                    hour = converted_date.strftime("%I:%M:%S %p")
                    code, quext_response = QuextTourService.save_quext_tour(
                        body)
                    if code != 200:
                        tour_error = quext_response["error"]["message"]
                        headers = {
                            'Access-Control-Allow-Origin': '*',
                            'Content-Type': 'application/json',
                        }
                        available_times = QuextTourService.get_available_times(
                            body["platformData"], body["tourScheduleData"]["start"], "Quext", headers)
                    else:
                        tour_scheduled_id = quext_response["data"]["id"]
                        tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'

        host = "http://{machineName}/api/applications/Integrations/RM/Leasing/GuestCard"

        

        
        


    def transform_payload(self, payload, ips):
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
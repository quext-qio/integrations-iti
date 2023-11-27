import json
import requests
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
import xml.etree.ElementTree as ET
from datetime import datetime
from services.shared.quext_tour_service import QuextTourService
from constants.mri_constants import *
from configuration.mri.mri_config import mri_config
from Converter import Converter


class MRIService(ServiceInterface):

    def get_data(self, body, ips, logger):
        logger.info(f"Getting data from MRI")

        available_times = []
        tour_scheduled_id = ""
        tour_error = ""
        appointment_date = ""
        tour_comment = ""

        # Save tour in Quext if it exists
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

        
        # Call MRI endpoint
        transformed_body = self.transform_payload_to_xml(body, ips, tour_comment)
        host = "https://mrix5pcapi.partners.mrisoftware.com/MRIAPIServices/api.asp?%24api=MRI_S-PMRM_GuestCardsBySiteID&%24format=xml" #TODO: Move this to a constant
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'request': 'application/xml',
            'Authorization': f'Basic {mri_config["mri_api_key"]}'
        }
        try:
            response = requests.request(
                "POST", 
                host, 
                headers=headers, 
                data=transformed_body,
            )
            logger.info(f"Status Code of Response: {response.status_code}")
            logger.info(f"Data of Response: {response.text}")
        except Exception as e:
            logger.error(f"Error trying to call MRI endpoint: {e}")

         # Success case
        tour_information = {
            "availableTimes": available_times,
            "tourScheduledID": tour_scheduled_id,
            "tourRequested": appointment_date,
            "tourSchedule": True if tour_scheduled_id else False,
            "tourError": tour_error
        }

        # Convert response from xml to json
        converter = Converter(response.text)
        response_as_json = converter.xml_to_json()
        response_as_dict = converter.json_to_dict(response_as_json)

        # Check if response is valid [Endpoint returns 200 even if there is an error]
        # If exists an error, return error message
        print(response_as_json)
        entry_response = response_as_dict["mri_s-pmrm_guestcardsbysiteid"]["entry"]
        if "Error" in entry_response:
            return {
                'statusCode': "400",
                'body': json.dumps({
                    'data': {},
                    'errors': {
                        'message': entry_response["Error"]["Message"]
                    }
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'isBase64Encoded': False
            }

        # Get prospect ID
        prospect_id = entry_response["NameID"]

        # Format response to return
        serviceResponse = ServiceResponse(
            guest_card_id=prospect_id,
            first_name=body["guest"]["first_name"],
            last_name=body["guest"]["last_name"],
            tour_information=tour_information,
        ).format_response()

        # Success response from MRI
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': serviceResponse,
                'errors': {}
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False
        }

    def transform_payload_to_xml(self, payload, ips, tour_comment):
        # Get visit date
        visit_date = ""
        if "tourScheduleData" in payload:
            visit_date = payload["tourScheduleData"]["start"][:
                                                              payload["tourScheduleData"]["start"].index("T")]

        # Get guest data
        guest = payload["guest"]
        guest_preference = payload["guestPreference"]

        # Map bedroom data
        bedroooms_data = []
        if "desiredBeds" in guest_preference:
            # Map string to int using [bedroom_mapping]
            for i in range(len(guest_preference["desiredBeds"])):
                string_beds = guest_preference["desiredBeds"][i]
                bedroooms_data.append(bedroom_mapping.get(string_beds, 0))
        bedrooms = str(max(bedroooms_data)) if len(bedroooms_data) > 0 else "0"
        move_in_date = payload["guestPreference"]["moveInDate"]

        # Create json body to be converted to xml and send to MRI
        json_body = {
            "mri_s-pmrm_guestcardsbysiteid": {
                "entry": {
                    "NameID": "",
                    "FirstName": guest["first_name"],
                    "LastName": guest["last_name"],
                    "PropertyID": ips["platformData"]["foreign_community_id"],
                    "Notes": payload["guestComment"] + f" {tour_comment}",
                    "Email": guest["email"],
                    "Phone": guest["phone"],
                    "Type": "P",  # TODO: Move this to a constant
                    "ProspectiveTenant": {
                        "entry": {
                            "DidNotLeaseReason": "",
                            "Beds": bedrooms,
                            "Baths": guest_preference["desiredBaths"][0],
                            "DesiredMoveInDate": move_in_date[:move_in_date.index("T")],
                            "TotalOccupants": f'{guest_preference["noOfOccupants"]}',
                            "DesiredLeaseTerm": f'{guest_preference["leaseTermMonths"]}',
                            "VisitDate": visit_date,
                        }
                    }
                }
            }
        }

        # Convert json to xml
        converter = Converter(json_body)
        return converter.json_to_xml()

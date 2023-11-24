import json
import requests
import os
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
import xml.etree.ElementTree as ET
from datetime import datetime
from services.shared.quext_tour_service import QuextTourService
from constants.mri_constants import *
from configuration.mri.mri_config import mri_config

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

        host = "https://mrix5pcapi.partners.mrisoftware.com/MRIAPIServices/api.asp?%24api=MRI_S-PMRM_GuestCardsBySiteID&%24format=xml"
        headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'request': 'application/xml',
                 'Authorization': f'Basic {mri_config["mri_api_key"]}'
        }
        try:
            response = requests.request("POST", host, headers=headers, data=transformed_body)
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

        prospect_id = "1" #TODO extract ID from response

        # Format response to return
        serviceResponse = ServiceResponse(
            guest_card_id=prospect_id,
            first_name=body["guest"]["first_name"],
            last_name=body["guest"]["last_name"],
            tour_information=tour_information,
        ).format_response()

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


    def transform_payload(self, payload, ips):
        move_in_date = payload["guestPreference"]["moveInDate"]
        visit_date = ""
        if "tourScheduleData" in payload:
            visit_date = payload["tourScheduleData"]["start"][: payload["tourScheduleData"]["start"].index("T")]


        root = ET.Element("mri_s-pmrm_guestcardsbysiteid")
        entry = ET.SubElement(root, "entry")

        # Assuming "guest" is the relevant part of the payload
        guest_data = payload.get("guest", {})
        guest_preference = payload.get("guestPreference", {})

        name_id = ET.SubElement(entry, "NameID")
        first_name = ET.SubElement(entry, "FirstName")
        last_name = ET.SubElement(entry, "LastName")
        property_id = ET.SubElement(entry, "PropertyID")
        notes = ET.SubElement(entry, "Notes")
        email = ET.SubElement(entry, "Email")
        phone = ET.SubElement(entry, "Phone")

        name_id.text = ""
        first_name.text = guest_data.get("first_name", "")
        last_name.text = guest_data.get("last_name", "")
        property_id.text = ""  # You can replace this with the actual property ID
        notes.text = payload.get("guestComment", "")
        email.text = guest_data.get("email", "")
        phone.text = guest_data.get("phone", "")

        p_type = ET.SubElement(entry, "Type")
        prospective_tenant = ET.SubElement(p_type, "ProspectiveTenant")
        tenant_entry = ET.SubElement(prospective_tenant, "entry")

        beds = ET.SubElement(tenant_entry, "Beds")
        baths = ET.SubElement(tenant_entry, "Baths")
        move_in_date = ET.SubElement(tenant_entry, "DesiredMoveInDate")
        total_occupants = ET.SubElement(tenant_entry, "TotalOccupants")
        desired_lease_term = ET.SubElement(tenant_entry, "DesiredLeaseTerm")
        visit_date = ET.SubElement(tenant_entry, "VisitDate")

        beds.text = "0.00"
        baths.text = guest_preference.get("desiredBaths")[0]
        move_in_date.text = guest_preference.get("moveInDate")[:guest_preference.get("moveInDate").index("T")]
        total_occupants.text = str(payload.get("guestPreference", {}).get("noOfOccupants", 0))
        desired_lease_term.text = guest_preference("leaseTermMonths", 0)
        visit_date.text = visit_date

        return ET.tostring(root, encoding="unicode")

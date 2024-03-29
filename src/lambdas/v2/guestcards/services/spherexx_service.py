import requests
import xml.etree.ElementTree as ET
import json
import re
import uuid
from datetime import datetime
from configuration.spherexx.spherexx_config import spherexx_config
from constants.spherexx_constants import *
from utils.shared.payload_handler import PayladHandler
from utils.service_response import ServiceResponse
from Converter import Converter


class SpherexxService:

    def get_data(self, body: dict, ips_response: dict, logger):
        logger.info(f"Getting data from Spherexx")
        prospect_comments = body["guestComment"] if "guestComment" in body else ""
        appointment_date = ""
        available_times = []
        tour_scheduled_id = None
        tour_error = ""
        first_contact = True
        tour_information = None
        property_id = ips_response["params"]["foreign_community_id"]
        community_name = ips_response["community"]["community_name"]
        move_in_date = body["guestPreference"].get("moveInDate")
        if move_in_date and "T" in move_in_date:
            body["guestPreference"]["moveInDate"] = move_in_date[0:move_in_date.index(
                "T")]
        else:
            body["guestPreference"]["moveInDate"] = None

        event = {
            "Source": body["source"],
            "EventType": "EmailFromProspect",
            "FirstContact": first_contact,
            "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "TransactionSourceid": "Quext",
            "Comments": prospect_comments,
            "UnitID": "",
        }

        events = PayladHandler().create_events(event, ips_response)
        if "tourScheduleData" in body:
            appointment_date = body["tourScheduleData"]["start"]
            if appointment_date != "":
                converted_date = datetime.strptime(appointment_date.replace(
                    "T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                format_date = converted_date.strftime("%B %d, %Y")
                hour = converted_date.strftime("%I:%M:%S %p")
                date_only = appointment_date[0:appointment_date.index("T")]
                available_times = self.get_appointment_slots(
                    property_id, date_only)

                if appointment_date[0:appointment_date.index("Z")].replace("T", " ") in available_times:
                    event = {
                        "Source": body["source"],
                        "EventType": "Appointment",
                        "FirstContact": first_contact,
                        "EventDate":  f'{appointment_date[0:appointment_date.index("Z")]}.000000-04:00',
                        "TransactionSourceid": "Quext",
                        "Comments": prospect_comments,
                        "UnitID": "",
                    }

                    events = PayladHandler().create_events(event, ips_response)
                    tour_scheduled_id = str(uuid.uuid4())
                    tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
                    prospect_comments = prospect_comments + tour_comment
                    available_times = []

                else:
                    tour_scheduled_id = ""
                    tour_error = "No time slots available for that start time"

                tour_information = {
                    "availableTimes": available_times,
                    "tourScheduledID": tour_scheduled_id,
                    "tourRequested": appointment_date,
                    "tourSchedule": True if tour_scheduled_id else False,
                    "tourError": tour_error
                }

        body_json = PayladHandler().builder_payload(body, events)

        body_json["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"].update({
            "Identification": [
                {
                    "@IDValue": community_name,
                    "@IDType": "PropertyName"
                },
                {
                    "@IDValue": property_id,
                    "@IDType": "PropertyID"
                }
            ]
        })

        xml = Converter(body_json).json_to_xml()
        cleaned_xml = re.sub(r'^<\?xml [^>]+>\s*', '', xml)
        url = f"{URL}{INSERT_LEAD_PATH}.asmx"
        username = spherexx_config["spherexx_username"]
        password = spherexx_config["spherexx_password"]
        sourceID = ips_response["params"]["sourceID"]
        payload = f'''<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                        <soap:Body>
                            <InsertLead xmlns="https://www.iloveleasing.com/">
                                <username>{username}</username>
                                <password>{password}</password>
                                <sourceID>{sourceID}</sourceID>
                                <XML_DATA><![CDATA[{cleaned_xml}]]>
                                </XML_DATA>
                                </InsertLead>
                                </soap:Body>
                                </soap:Envelope>'''
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': f'https://www.iloveleasing.com/InsertLead'
        }
        res = requests.request("POST", url, headers=headers, data=payload)

        # Format response of Spherexx
        is_success = True if "true" in res.text else False
        status_code = "200" if is_success else "400"
        error_message = "The Data sent is invalid"
        serviceResponse = ServiceResponse(
            guest_card_id=str(uuid.uuid4()) if is_success else "",
            first_name=body["guest"]["first_name"],
            last_name=body["guest"]["last_name"],
            message="" if is_success else error_message,
            result="SUCCESS" if is_success else "FAILURE",
            tour_information=tour_information,
        ).format_response()

        if status_code != "200":
            logger.error(f"Error from Spherexx Guestcard: {error_message}")
        return {
            'statusCode': status_code,
            'body': json.dumps({
                'data': serviceResponse,
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'isBase64Encoded': False
        }

    def get_appointment_slots(self, property_id, start_date):
        url = f"{URL}GetOpenSlots.asmx"
        username = spherexx_config["spherexx_username"]
        password = spherexx_config["spherexx_password"]

        payload = f'''<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                    <soap:Body>
                        <GetOpenAppointmentSlots xmlns="http://www.iloveleasing.com">
                        <username>{username}</username>
                        <password>{password}</password>
                        <property>{property_id}</property>
                        <startDate>{start_date}</startDate>
                        </GetOpenAppointmentSlots>
                    </soap:Body>
                    </soap:Envelope>'''
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://www.iloveleasing.com/GetOpenAppointmentSlots'
        }
        res = requests.request("POST", url, headers=headers, data=payload)
        root = ET.fromstring(res.text)
        cdata = root.find(
            ".//{http://www.iloveleasing.com}GetOpenAppointmentSlotsResult").text

        # Parse the inner result XML
        inner_root = ET.fromstring(cdata)

        # Extract Slot elements
        slots = inner_root.findall(".//Slot")

        # Extract available times and create a list
        available_times = [slot.attrib["Date"] + " " +
                           slot.attrib["time"] for slot in slots]

        # Convert the date format to match "YYYY-MM-DD HH:MM:SS" format
        formatted_times = [datetime.strptime(
            time, "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S") for time in available_times]

        return formatted_times

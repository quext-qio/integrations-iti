import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from configuration.spherexx.spherexx_config import spherexx_config
from constants.spherexx_constants import *
from utils.shared.payload_handler import PayladHandler
from Converter import Converter

class SpherexxService:

    def get_data(self, body: dict, ips_response: dict):
        prospect_comments = body["guestComment"] if "guestComment" in body else ""
        format_date = ""
        hour = ""
        appointment_date = ""
        available_times = []
        tour_scheduled_id = None
        tour_error = ""
        first_contact =  True

        event = {
                    "Source": body["source"],
                    "EventType": "WalkIn",
                    "FirstContact": first_contact,
                    "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "TransactionSourceid": "",
                    "UnitID": "",
                }
        tour_information = {
                    "availableTimes": available_times,
                    "tourScheduledID": tour_scheduled_id,
                    "tourRequested": appointment_date,
                    "tourSchedule": True if tour_scheduled_id else False,
                    "tourError": tour_error
                }
        
        events = PayladHandler().create_events(event, ips_response)
       
        if "tourScheduleData" in body:
            appointment_date = body["tourScheduleData"]["start"]
            if appointment_date != "":
                event = {
                    "Source": body["source"],
                    "EventType": "WalkIn",
                    "FirstContact": first_contact,
                    "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "TransactionSourceid": "Quext",
                    "UnitID": "",
                }

        
        xml = Converter(PayladHandler().builder_payload(body, events)).json_to_xml()
        print(xml)

    

    def get_agents(self):
        pass

    def get_appointment_slots(self, property_id, start_date):
        url = f"{URL}/GetOpenSlots.asmx"
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
        'SOAPAction': 'http://{HOST}/{SLOTS_PATH}'
        }

        res = requests.request("POST", url, headers=headers, data=payload)
        root = ET.fromstring(res.text)
        cdata = root.find(f".//http://{HOST}/GetOpenAppointmentSlotsResult").text

        # Parse the inner result XML
        inner_root = ET.fromstring(cdata)

        # Extract Slot elements
        slots = inner_root.findall(".//Slot")

        # Extract available times and create a list
        available_times = [slot.attrib["Date"] + " " + slot.attrib["time"] for slot in slots]

        # Convert the date format to match "YYYY-MM-DD HH:MM:SS" format
        formatted_times = [datetime.strptime(time, "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S") for time in available_times]

        # Create the JSON-like dictionary
        result = {
            "data": {
                "availableTimes": formatted_times
            },
            "error": {}
        }

        # Convert the result dictionary to JSON-like string
        json_result = json.dumps(result, indent=4)
        return  json_result

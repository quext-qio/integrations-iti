import requests
from datetime import datetime
from Utils.Constants.SpherexxConstants import *
from configuration.spherexx_config import spherexx_config
import xml.etree.ElementTree as ET


class DataSpherexx:

        def get_tour_availability(self, ips, event):
                url = f"{URL}GetOpenSlots.asmx"
                username = spherexx_config["spherexx_username"]
                password = spherexx_config["spherexx_password"]

                payload = f'''<?xml version="1.0" encoding="utf-8"?>
                            <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                            <soap:Body>
                                <GetOpenAppointmentSlots xmlns="http://www.iloveleasing.com">
                                <username>{username}</username>
                                <password>{password}</password>
                                <property>{ips["platformData"]["foreign_community_id"]}</property>
                                <startDate>{event["timeData"]["fromDate"]}</startDate>
                                </GetOpenAppointmentSlots>
                            </soap:Body>
                            </soap:Envelope>'''
                headers = {
                'Content-Type': 'text/xml; charset=utf-8',
                'SOAPAction': 'http://www.iloveleasing.com/GetOpenAppointmentSlots'
                }
                res = requests.request("POST", url, headers=headers, data=payload)
                root = ET.fromstring(res.text)
                cdata = root.find(".//{http://www.iloveleasing.com}GetOpenAppointmentSlotsResult").text


                # Parse the inner result XML
                inner_root = ET.fromstring(cdata)

                # Extract Slot elements
                slots = inner_root.findall(".//Slot")

                # Extract available times and create a list
                available_times = [slot.attrib["Date"] + " " + slot.attrib["time"] for slot in slots]

                # Convert the date format to match "YYYY-MM-DD HH:MM:SS" format
                formatted_times = [datetime.strptime(time, "%m/%d/%Y %I:%M %p").strftime("%Y-%m-%d %H:%M:%S") for time in available_times]

                return  formatted_times, {}

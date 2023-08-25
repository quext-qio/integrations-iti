import json, requests, logging
from datetime import datetime, timedelta
from abstract.service_interface import ServiceInterface
from constants.yardi_constants import YardiConstants
from Converter import Converter
from configuration.yardi.yardi_config import config as yardiConfig
from utils.shared.payload_handler import PayladHandler
from services.shared.quext_tour_service import QuextTourService
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
import xml.etree.ElementTree as ET
import hashlib
import base64

class YardiService(ServiceInterface):

    def get_data(self, body: dict, ips_response: dict):
            platform_name = ips_response["platformData"]["platform"]
            is_qa = True if platform_name == "Yardi Demo" else False
            tour_information = None
            property_id = ips_response["platformData"]["foreign_community_id"]
            customer_info = body["guest"]
            guest_preference = body["guestPreference"]
            community_uuid = body["platformData"].get(YardiConstants.COMMUNITYUUID)
            customer_uuid =  body["platformData"].get(YardiConstants.CUSTOMERUUID)
            
            first_contact, generated_id = self.generate_unique_id(body.get(YardiConstants.QCONTACTID), community_uuid, customer_uuid)
            customer_info["Identification"] = [
                {
                    "@IDValue": generated_id,
                    "@IDType": YardiConstants.PROSPECT_ID,
                    "@OrganizationName": YardiConstants.ORGANIZATION_NAME
                },
                {
                    "@IDValue": property_id,
                    "@IDType": YardiConstants.PROPERTY_ID,
                    "@OrganizationName": YardiConstants.YARDI
                }
            ]
            
            phone = self.clean_and_validate_phone_number("+"+customer_info[phone])
            customer_info["guest"]["phone"] = phone
            bedroooms_data = []
            if "desiredBeds" in guest_preference:
                # Map string to int using [bedroom_mapping]
                for i in range(len(guest_preference["desiredBeds"])):
                    string_beds = guest_preference["desiredBeds"][i]
                    bedroooms_data.append(bedroom_mapping.get(string_beds, 0))
            event = {
                    "Source": body["source"],
                    "EventType": "Webservice",
                    "FirstContact": first_contact,
                    "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "TransactionSourceid": YardiConstants.SOURCE,
                    "UnitID": "",
                }
            
            event_object = PayladHandler().create_events(event, ips_response)
         
            if "tourScheduleData" in body:
                appointment_date = body["tourScheduleData"]["start"]
                comments = "Guest Card submitted online "
                if appointment_date != "":
                    converted_date = datetime.strptime(appointment_date.replace("T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                    format_date = converted_date.strftime("%B %d, %Y")
                    hour = converted_date.strftime("%I:%M:%S %p")
                    code,quext_response = QuextTourService.save_quext_tour(body)
                    if code != 200:
                        tour_requested = appointment_date
                        tour_error = quext_response["error"]["message"]
                        available_times =  QuextTourService.get_available_times(body["platformData"], body["tourScheduleData"]["start"], "Quext", headers)
                        
                    else:
                        tour_schedule = True
                        tour_requested = appointment_date
                        tour_scheduled_id = quext_response.get("data", {}).get("id", "")
                        actual_customer_comment = body.get("guestComment", "")
                        tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
                        body["guestComment"] = actual_customer_comment + tour_comment
                        purpose_exists = self.search_purpose("appointmentNotification", community_uuid)
                        comments= f'Guest Card submitted online with Tour Appointment Scheduled for {format_date} at {hour}.'
                        desired_rent = body["guestPreference"].get("desiredRent", "")
                        if desired_rent != "":
                            comments += f' Preferences: Max rent-> {desired_rent} '
                            body["guestComment"] += f' Preferences: Max rent-> {body["guestPreference"]["desiredRent"]} '
                        if purpose_exists:
                            input_time = datetime.strptime(tour_requested[tour_requested.index("T") + 1: tour_requested.index("Z")], "%H:%M:%S")
                            formatted_time = input_time.strftime("%H:%M:%S")
                            unit_id = self.get_unit_id(desired_rent, max(bedroooms_data) if len(bedroooms_data) > 0 else 0, tour_requested, property_id, is_qa)
                            event_list = []
                            if unit_id is None:
                                event_list = self.get_events(event_object=event_object, date_tour=tour_requested[0: tour_requested.index("T")] + "T" + formatted_time, tour_comment=tour_comment, unit_id=None)
                            else:
                                event_list = self.get_events(event_object=event_object, date_tour=tour_requested[0: tour_requested.index("T")] + "T" + formatted_time, tour_comment=tour_comment, unit_id=unit_id)
                            body["xml"]["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"] = event_list
                
                tour_information = {
                        "availableTimes": available_times,
                        "tourScheduledID": tour_scheduled_id,
                        "tourRequested": appointment_date,
                        "tourSchedule": True if tour_scheduled_id else False,
                        "tourError": tour_error
                    }
          
            xml = Converter(PayladHandler().builder_payload(body, event_list)).json_to_xml()
          
            # Create body for Yardi
            import_yardi_guest_login = {
                "@xmlns": YardiConstants.XMLNS,
                "UserName": yardiConfig[YardiConstants.USERNAME_DEMO] if is_qa else yardiConfig[YardiConstants.USERNAME],
                "Password": yardiConfig[YardiConstants.PASSWORD_DEMO] if is_qa else yardiConfig[YardiConstants.PASSWORD],
                "ServerName": yardiConfig[YardiConstants.SERVER_NAME_DEMO] if is_qa else yardiConfig[YardiConstants.SERVER_NAME],
                "Database": yardiConfig[YardiConstants.DATABASE_DEMO] if is_qa else yardiConfig[YardiConstants.DATABASE],
                "Platform": YardiConstants.YARDI_PLATFORM,
                "InterfaceEntity": YardiConstants.YARDI_INTERFACE_ENTITY,
                "InterfaceLicense": yardiConfig[YardiConstants.INTERFACE_LICENSE_DEMO] if is_qa else yardiConfig[YardiConstants.INTERFACE_LICENSE],
                "XmlDoc": xml
            }
            new_body = {
                "soap:Envelope": {
                    "@xmlns:soap": YardiConstants.XMLSOAP,
                    "soap:Body": {
                    "ImportYardiGuest_Login": import_yardi_guest_login,
                    }
                }
            }
                # Call the outgoing
            try:
                    url = yardiConfig["yardi_url_demo"] if is_qa else yardiConfig["yardi_url"]
                    headers = {
                    'Content-Type': 'text/xml; charset=utf-8',
                    'SOAPAction': YardiConstants.GUEST_CARD_SOAP
                    }
                    response = requests.request("POST", url, headers=headers, data=xml)
                    response = json.loads(Converter(response.text).xml_to_json())
                    messages = response.get('soap:Envelope', {}).get('soap:Body', {}).get('ImportYardiGuest_LoginResponse', {}).get('ImportYardiGuest_LoginResult', {}).get('Messages', {}).get('Message', [])

                    customer_id = None
                    if "@messageType" in messages:
                        if messages["@messageType"] == "Error":
                            logging.error(f"{self.handle_POST.__qualname__} Error trying to call Yardi outgoing{messages.get('#text', '')}")
                            return  {
                                'statusCode': "500",
                                'body': json.dumps({
                                    'data': [],
                                    'errors': [{"message": f"Error trying to call Yardi outgoing: {messages.get('#text', '')}"}],
                                }),
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',  
                                },
                                'isBase64Encoded': False  
                            }

                    for message in messages:
                        if "#text" in message:
                            if 'CustomerID' in message['#text']:
                                customer_id = message['#text'].split(': ')[1]

                    serviceResponse = ServiceResponse(
                        guest_card_id= customer_id,
                        first_name=body["guest"]["first_name"],
                        last_name=body["guest"]["last_name"],
                        tour_information=tour_information,
                    ).format_response()

                    return  {
                                'statusCode': "200",
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
    
                    
            except Exception as e:
                    logging.error(f"{self.handle_POST.__qualname__} Error trying to call Yardi outgoing{e}")
                    return {
                        'statusCode': "500",
                        'body': json.dumps({
                            'data': [],
                            'errors': [{"message": f"Unhandled error from Yardi guestcard: {e}"}]
                        }),
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',  
                        },
                        'isBase64Encoded': False  
                    }
        

    #Define function to seach the generated Yardi ID into Leasing Database
    def search_partner_id(self, partnerId, thing_type, partner_use_id):

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = json.dumps({
            "partner_id": partnerId,
            "thing_type": thing_type,
            "partner_use_id": [
                partner_use_id
            ]
        })
        response = requests.post(f'{yardiConfig["leasing_url"]}/api/v1/partner-id-translation/lookup', headers=headers, data = payload)
       
        return True if len(json.loads(response.text)) > 0 else False

    #Seach Yardi partner_id in IPS
    def get_yardi_partner_id(self):
        response = requests.get(f'{yardiConfig["ips_host"]}/api/partners')
        partners_info = response.json()

        # find the first object that matches the filter condition
        partner_uuid = next((partner for partner in partners_info["content"] if partner['name'] == 'Yardi'), None)
        
        return partner_uuid["uuid"]

  # Define function to generate unique ID from three UUIDs
    def generate_unique_id(self, qContactUUID, communityUUID, customerUUID):
        """
        This function generates a unique 20-character string by concatenating three UUIDs
        and hashing the resulting byte string using SHA-256.
        """
        # Concatenate the three UUIDs and convert to bytes
        id_bytes = str(qContactUUID).encode()
        
        # Apply SHA-256 hash function and take first 10 bytes of resulting digest (20 characters)
        hash_value = hashlib.sha256(id_bytes).digest()[:10]
        
        # Encode hash value using base64 and convert to UTF-8 string
        unique_id = base64.urlsafe_b64encode(hash_value).decode('utf-8')
        partner_id = self.get_yardi_partner_id()
        first_contact = "false"
        exists_id = self.search_partner_id(partner_id, YardiConstants.THING_TYPE, unique_id)
    
        if not exists_id:
            first_contact = "true"
            register_response = self.register_partner_id(partner_id, customerUUID, communityUUID, YardiConstants.THING_TYPE, unique_id)
            if register_response:
                logging.info(f"Leasing register new partner_id response: {register_response}")
        # Return the unique ID
        return first_contact, unique_id  
    
    
    def clean_and_validate_phone_number(self, number):
        """
        Cleans and validates US phone number using regular expression.
        Returns cleaned phone number if valid, otherwise returns None.
        """
        # Regular expression pattern for US phone numbers
        pattern = re.compile(r'^(\+1)?[\s-]?\(?(\d{3})\)?[\s-]?(\d{3})[\s-]?(\d{4})$')
        # Check if the number matches the pattern
        match = pattern.match(number)
        if not match:
            return None
        # Extract and format the phone number components
        country_code = match.group(1)
        area_code = match.group(2)
        prefix = match.group(3)
        suffix = match.group(4)
        # Clean the phone number by removing country code and non-digit characters
        phone_number = f"{area_code}-{prefix}-{suffix}"
        # Return the cleaned phone number
        return phone_number
    
    
     #search for Unit ID  in Unified Data model data base
    def get_unit_id(self, desired_rent, num_bedrooms, propertyID, is_qa):
        url = yardiConfig["yardi_url_demo"] if is_qa else yardiConfig["yardi_url"]
        yardi_payload = {
                    "@xmlns": YardiConstants.XMLNS,
                    "UserName": yardiConfig[YardiConstants.USERNAME_DEMO] if is_qa else yardiConfig[YardiConstants.USERNAME],
                    "Password": yardiConfig[YardiConstants.PASSWORD_DEMO] if is_qa else yardiConfig[YardiConstants.PASSWORD],
                    "ServerName": yardiConfig[YardiConstants.SERVER_NAME_DEMO] if is_qa else yardiConfig[YardiConstants.SERVER_NAME],
                    "Database": yardiConfig[YardiConstants.DATABASE_DEMO] if is_qa else yardiConfig[YardiConstants.DATABASE],
                    "Platform": YardiConstants.YARDI_PLATFORM,
                    "InterfaceEntity": YardiConstants.YARDI_INTERFACE_ENTITY,
                    "InterfaceLicense": yardiConfig[YardiConstants.INTERFACE_LICENSE_DEMO] if is_qa else yardiConfig[YardiConstants.INTERFACE_LICENSE],
                    "YardiPropertyId": propertyID
                }
                
        new_body = {
                    "soap:Envelope": {
                        "@xmlns:soap": YardiConstants.XMLSOAP,
                        "soap:Body": {
                        "UnitAvailability_Login": yardi_payload,
                        }
                    }
                }
        try:
            xml = Converter(json.dumps(new_body)).json_to_xml()

            headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': YardiConstants.UNITS_SOUP
            }
            response = requests.request("POST", url, headers=headers, data=xml)
        
            xml_string =f'''{response.text}'''
            root = ET.fromstring(xml_string)
            # Find all ILS_Unit elements
            ils_units = root.findall('.//ILS_Unit')
            unit_id = None
            # Iterate over each ILS_Unit element
            for ils_unit in ils_units:
                # Find the value of UnitEconomicStatus within the ILS_Unit element
                if(int(float(ils_unit.find('.//MarketRent').text)) <= int(desired_rent)) and  (int(float(ils_unit.find('.//UnitBedrooms').text)) >= int(num_bedrooms)):
                    unit_economic_status = ils_unit.find('.//UnitEconomicStatus').text
                    if unit_economic_status == "model" or unit_economic_status == "residential":
                        identification_element = root.find('.//ILS_Unit')
                        # Retrieve the value of the IDValue attribute
                        unit_id = identification_element.get('IDValue')

            return unit_id
        except Exception as e:
            logging.error(f"{self.handle_POST.__qualname__} Yardi {HTTP_SERVER_ERROR_MSJ}: {e}")
            self.response.status_code = 504
            self.response.payload = {
                "data": [],
                "errors": [{"message": f"{HTTP_SERVER_ERROR_MSJ}"}],
            }

   #Add Guided  tour event
    def get_events(self, event_object, date_tour, tour_comment, unit_id: None):
        new_date = event_object["@EventDate"][0: event_object["@EventDate"].index("T")+1]
        event_object.update({"@EventDate": new_date+ "07:00:00"})
        events_list = [event_object]
        if unit_id:
             events_list.append({"@EventType": "Appointment",
                            "@EventDate": date_tour,
                            "EventID": {
                                "@IDValue": "",
                                "@IDType":  unit_id
                            },
                            "Agent": {
                                "AgentName": {
                                    "FirstName": event_object[YardiConstants.AGENT][YardiConstants.AGENT_NAME]["FirstName"],
                                    "LastName": event_object[YardiConstants.AGENT][YardiConstants.AGENT_NAME]["LastName"]
                                }
                            },
                            "FirstContact": "false",
                            "Comments":  tour_comment
                            }) 
        else:
             events_list.append({"@EventType": "GuidedTour",
                            "@EventDate": date_tour,
                            "EventID": {
                                "@IDValue": "",
                                "@IDType": YardiConstants.EVENT_ID
                            },
                            "Agent": {
                                "AgentName": {
                                    "FirstName": event_object[YardiConstants.AGENT][YardiConstants.AGENT_NAME]["FirstName"],
                                    "LastName": event_object[YardiConstants.AGENT][YardiConstants.AGENT_NAME]["LastName"]
                                }
                            },
                            "FirstContact": "false",
                            "Comments":  tour_comment
                            }) 
        return events_list 
            
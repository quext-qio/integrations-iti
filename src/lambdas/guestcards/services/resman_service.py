import json, requests, logging
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.shared.config import config
from utils.shared.payload_handler import PayladHandler
from services.shared.quext_tour_service import QuextTourService
from utils.shared.constants.resman_constants import *
from Converter import Converter
from utils.service_response import ServiceResponse

class ResManService(ServiceInterface):

    def get_data(self, body, ips):
          # Get credentials information
            integration_partner_id = config['Integration_partner_id']
            api_key = config['ApiKey']
            account_id = config["resman_account_id"]
            available_times = []
            tour_scheduled_id = ""
            tour_error = ""
            appointment_date = ""
                
            try:
                # If IPS doesn't return the foreign_community_id show the error
                resman_params = {
                    "IntegrationPartnerID": f"{integration_partner_id}",
                    "APIKey": f"{api_key}",
                    "AccountID": f"{account_id}",
                    "PropertyID": f"{ips['platformData']['foreign_community_id']}"
                }
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'request': 'application/xml'
                }
                url = "https://api.myresman.com/Leasing/GetProspectSources"
                outgoing_prospect_source = requests.request("POST", url, headers=headers, data=resman_params)
              
                prospects_list = json.loads(outgoing_prospect_source.text)
                prospectSourceId = ""
                tour_comment = ""
                first_contact = True
                #Seach the prospectSourceID 
                for prospect in prospects_list["ProspectSources"]:
                    if prospect["Name"] == "Quext":
                        prospectSourceId = prospect["ID"] 
                
                
                #event_obj = xml_payload['xml']["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                event = {
                    "Source": body["source"],
                    "EventType": "WalkIn",
                    "FirstContact": first_contact,
                    "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "TransactionSourceid": prospectSourceId,
                    "UnitID": "",
                }

                if "tourScheduleData" in body:
                    appointment_date = body["tourScheduleData"]["start"]
                    if appointment_date != "":
                        converted_date = datetime.strptime(appointment_date.replace("T", " ")[0:appointment_date.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                        format_date = converted_date.strftime("%B %d, %Y")
                        hour = converted_date.strftime("%I:%M:%S %p")
                        code, quext_response = QuextTourService.save_quext_tour(body)
                        if code != 200:
                            tour_error = quext_response["error"]["message"]
                            headers = {
                                'Access-Control-Allow-Origin': '*',
                                'Content-Type': 'application/json',
                            }
                            available_times = QuextTourService.get_available_times(body["platformData"], body["tourScheduleData"]["start"], "Quext", headers)
                        else:
                            tour_scheduled_id = quext_response["data"]["id"]
                            tour_comment = f' --TOURS--Tour Scheduled for {format_date} at {hour}'
                            prospect_comments = prospect_comments + tour_comment

                # If the prospect is completely new
                # Create body for resman
                tour_information = {
                    "availableTimes": available_times,
                    "tourScheduledID": tour_scheduled_id,
                    "tourRequested": appointment_date,
                    "tourSchedule": True if tour_scheduled_id else False,
                    "tourError": tour_error
                }
                xml = Converter(PayladHandler().builder_payload(body, PayladHandler().create_events(event, ips))).json_to_xml()
                #xml = Converter(json.dumps(json_to_convert_xml)).json_to_xml()
                resman_params.update({"Xml": xml})
                print(xml)

                # Call the outgoing
                #TODO: Change the url to the correct one
                response = self.save_prospect(xml, ips, body["guest"]["first_name"],body["guest"]["last_name"], tour_information)
                # If the response is not success, start testing all scenarios
                if response[RESMAN][STATUS] != "Success":
                    # Consult if prospect exists by email
                    del resman_params["Xml"]
                    resman_params.update({"email": body["guest"]["email"]})
                    new_event = PayladHandler().create_events({
                        "Source": body["source"],
                        "EventType": "WalkIn",
                        "FirstContact": first_contact,
                        "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "TransactionSourceid": prospectSourceId,
                        "UnitID": ""
                        }, ips)
                    get_response = self.search_prospects(self, resman_params)
                    
                    # If the email was found, build a new xml add the new event to the found prospect
                    if get_response["data"][0][LEADMANAGEMENT][PROSPECTS] != None: 
                        #Xml 
                        # new_event = xml_payload['xml']["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                        new_xml = get_response["data"][0]
                        event_found = new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                        event_to_modify = event_found
                        #order events list By date
                        
                        if type(event_found) == list:
                            event_found.sort(key = lambda x: datetime.strptime(x['@EventDate'][0:x['@EventDate'].index("T")], '%Y-%m-%d'), reverse = True)
                            event_to_modify  = event_found[0]

                        #Verify if event comments already contains tour information  
                        is_new, event_modified, message = self.verify_event_fields(event_to_modify, event_to_modify["@EventDate"], event_to_modify["Comments"], tour_comment)
                        # Compare 2 phone numbers
                        if is_new:
                            new_phone_number = body['guest']['phone']
                            phone_number_found = get_response["data"][0]["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"]
                            first_contact = False
                            
                            if new_phone_number != phone_number_found:
                                # add phone number to event, also update
                                actual_comment += f" *Phone: {new_phone_number}"
    
                            #new_event.update({"Comments": actual_comment})
                            new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"] = new_phone_number

                            #If the Events in the result is a list is going to append the new event
                            if type(event_found) == list:
                                event_found.append(new_event)
                            #if not, transform the dict to List (adding the new event)
                            else:
                                new_list = [event_found, new_event]
                                new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]= new_list
                        else:
                            if message == "":
                                new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"].update({"Event": event_modified})
                            else :
                                tour_error = message
                                new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"].update({"Event": event_modified})
                                available_times = []

                        # Payload to update
                        payload = {
                            "customerUUID": self.request.payload['customerUUID'], 
                            "communityUUID": self.request.payload['communityUUID'], 
                            "xml": new_xml
                        }
                        prospect_updated = self.update_prospect(payload,ips, body["guest"]["first_name"],body["guest"]["last_name"], tour_information)
                        if len(prospect_updated["errors"]) != 0:
                            new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"] = ""
                            payload["xml"]=new_xml
                            event = new_xml['xml']["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                            event.update({"Comments": event['Comments'] if "Comments" in new_event else "" + tour_comment})
                            return self.update_prospect(payload, ips, body["guest"]["first_name"],body["guest"]["last_name"], tour_information)
                        else: 
                            return prospect_updated   

                # Success case
                return self.get_response(response[RESMAN][RESPONSE], ips, body["guest"]["first_name"],body["guest"]["last_name"], tour_information )
             
             
        
            except Exception as e:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'data': {},
                        'errors': {"message": f"{e}"},
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',  
                    },
                    'isBase64Encoded': False  
                }


    def verify_event_fields(self,json_to_verify, date, actual_comment, tour_comment):
            #Ask if EventDate is today date, if so, update the comment with tour info, if not, create a new event
            message = ""
            event = json_to_verify
            is_new = False
            actual_comment = actual_comment if actual_comment != None else ""
    
            if str(datetime.utcnow().strftime("%Y-%m-%d")) in date:
                    if actual_comment != "" and "--TOURS--" in actual_comment:
                        is_new = False
                        message = "Guest Card and Scheduled a Tour have already been submitted"
                    else:
                        is_new = False
                        event.update({"Comments": tour_comment})
                    
            else:
                    is_new = True
                    
            return is_new, event, message
    

    def search_prospects(self, payload):
        # API endpoint URL
        url = "https://api.myresman.com/MITS/SearchProspects"

        # Headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'request': 'application/xml'
            }
        # Request payload (if required by the API, adjust it accordingly)
     
        try:
            # Make the API request
            response = requests.post(url, data=payload, headers=headers)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # The API response will be in JSON format, you can access it using response.json()
                api_data = response.json()
                logging.info(api_data)
            else:
                logging.error(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error making the request: {e}")

    
    
    def save_prospect(self, payload, ips, name, last_name, tour_info):
        # TODO: Implement unique method for save prospects
        print("Save prospect")
        integration_partner_id = config['Integration_partner_id']
        api_key = config['ApiKey']
        account_id = config["resman_account_id"]
        try:
        # Create body for resman
            
            data = {
                "IntegrationPartnerID": f"{integration_partner_id}",
                "APIKey": f"{api_key}",
                "AccountID": f"{account_id}",
                "PropertyID": f"{ips['platformData']['foreign_community_id']}",
                "Xml": payload
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'request': 'application/xml'
            }
            print("267")
            url = "https://api.myresman.com/MITS/PostLeadManagement4_0"
            outgoing_save_prospect = requests.request("POST", url, headers=headers, data=data)
            response = json.loads(Converter(outgoing_save_prospect.text).xml_to_json())

            if response[RESMAN][STATUS] != "Success":
                error = response[RESMAN][ERROR_DESCRIPTION]
                print(f"Unhandled Error in RESMAN Guestcard: {error}")
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'data': {},
                        'errors': {"message": f"{error}"},
                    }),
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',  
                    },
                    'isBase64Encoded': False  
                }

            # Success case
            return response
        
        except Exception as e:
            print(f"Unhandled Error in RESMAN Guestcard: {e}")
            return {
                'statusCode': 504,
                'body': json.dumps({
                    'data': {},
                    'errors': {"message": f"{e}"},
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False  
            }

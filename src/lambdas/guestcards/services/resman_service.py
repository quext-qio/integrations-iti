import json, requests, logging
from datetime import datetime
from abstract.service_interface import ServiceInterface
from Utils.shared.config import config
from Utils.shared.payload_handler import PayladHandler
from Converter import Converter

class ResManService(ServiceInterface):
    
    def get_data(self, body, ips):
          # Get credentials information
            integration_partner_id = config['Integration_partner_id']
            api_key = config['ApiKey']
            account_id = config["resman_property_id"]
            
            try:
                # If IPS doesn't return the foreign_community_id show the error
                if not "foreign_community_id" in ips["platformData"]:
                    self.response.status_code = 404
                    return [], [{"message": f"foreign_community_id, Not Found"}]

                #Validate prospect source
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
                
                xml_payload = Converter(PayladHandler().builder_payload(body,)).to_xml()
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
                        hour = f'{converted_date.hour}:{converted_date.minute}'
                        code,quext_response = self.save_quext_tour(xml_payload)
                        if code != 200:
                            tour_requested = appointment_date
                            tour_error = quext_response["error"]["message"]
                            available_times = self.get_available_times(body.get("platformData"), appointment_date, "Quext", headers)
                        else:
                            tour_schedule = True
                            tour_scheduled_id = quext_response["data"]["id"]
                            actual_comment = body["guestComment"] if "guestComment" in body else ""
                            tour_comment = "--TOURS--Tour Scheduled for " + format_date + " at " + hour

                # If the prospect is completely new
                # Create body for resman
                
                json_to_convert_xml = xml_payload['xml']
                xml = Converter(json.dumps(json_to_convert_xml)).json_to_xml()
                resman_params.update({"Xml": xml})

                # Call the outgoing
                #TODO: Change the url to the correct one
                url = "https://api.myresman.com/Leasing/SaveProspect"
                outgoing_response = requests.request("POST", url, headers=headers, data=resman_params)
                response = json.loads(Converter(outgoing_response.text).xml_to_json())

                # If the response is not success, start testing all scenarios
                if response[RESMAN][STATUS] != "Success":
                    # Consult if prospect exists by email
                    del resman_params["Xml"]
                    resman_params.update({"email": body["guest"]["email"]})
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

                        #TODO: Verify if this line is necessary
                        is_new, event_modified, message = self.verify_event_fields(event_to_modify, new_event["@EventDate"], event_found["Comments"], tour_comment)
                        # Compare 2 phone numbers
                        if is_new:
                            new_phone_number = xml_payload['guest']['phone']
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
                        prospect_updated = self.update_prospect(payload, credentials, available_times, tour_requested, tour_schedule,
                                                                tour_scheduled_id, tour_error)
                        if len(prospect_updated["errors"]) != 0:
                            new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"] = ""
                            payload["xml"]=new_xml
                            event = new_xml['xml']["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                            event.update({"Comments": event['Comments'] if "Comments" in new_event else "" + tour_comment})
                            return self.update_prospect(payload, credentials, available_times, tour_requested, tour_schedule,
                                                        tour_scheduled_id, tour_error)
                        else: 
                            return prospect_updated   

                # Success case
                self.response.status_code = HTTP_OK_CODE
                self.response.payload = self.get_response(response[RESMAN][RESPONSE],available_times, tour_schedule, tour_scheduled_id, tour_requested, tour_error, "" )
                return
             
        
            except Exception as e:
               return  [], [{"message": f"{e}"}],

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
                print(response.text)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error making the request: {e}")

    def update_prospect(self, payload, credentials, available_times, tour_requested, tour_schedule, tour_scheduled_id, tour_error):
        headers = Headers(methods='OPTIONS, HEAD, POST, GET, PATCH')
        self.response.status_code = HTTP_OK_CODE
        self.response.headers = headers.get()

        # Get credentials information
        integration_partner_id = credentials["body"]["IntegrationPartnerID"]
        api_key = credentials["body"]["ApiKey"]
        account_id = credentials["body"]["AccountID"]
        self.logger.info(f"Credentials: {integration_partner_id}, {api_key}, {account_id}, {credentials}")

        # Check the body of the request
        body = {} if payload == "" else payload
        is_valid, input_errors = SchemaRequestPost(body).is_valid()
        if not is_valid:
            self.response.status_code = HTTP_BAD_REQUEST_CODE
            errors = [{"message": f"{k}, {v[0]}"} for k, v in input_errors.items()]
            response = {
                "data": [],
                "errors": errors
            }
            self.response.payload = response
            return response

        try:
            # Get propertyId from IPS
            _payload = { 
                "customerUUID": self.request.payload['customerUUID'], 
                "communityUUID": self.request.payload['communityUUID'], 
                "purpose": "guestCards" 
            }
            outgoingIPSChannel = self.outgoing.plain_http['Integrated Partner Storage [Purposes] (Internal)']
            outgoingIPSChannelResponse = outgoingIPSChannel.conn.get(self.cid, _payload)
            ips_response = json.loads(outgoingIPSChannelResponse.text)

            # If IPS returns an error
            if "error" in ips_response:
                self.response.status_code = outgoingIPSChannelResponse.status_code
                response = {
                    "data": [],
                    "errors": [{"message": f"{ips_response['error']}"}],
                }
                self.response.payload = response
                return response

            # If IPS doesn't return the foreign_community_id show the error
            if not "foreign_community_id" in ips_response["platformData"]:
                self.response.status_code = 404
                reponse = {
                    "data": [],
                    "errors": [{"message": f"foreign_community_id, Not Found"}],
                }
                self.response.payload = reponse
                return reponse

            # Create body for resman
            json_to_convert_xml = payload['xml']
            xml = Converter(json.dumps(json_to_convert_xml)).json_to_xml()
            data = {
                "IntegrationPartnerID": f"{integration_partner_id}",
                "APIKey": f"{api_key}",
                "AccountID": f"{account_id}",
                "PropertyID": f"{ips_response['platformData']['foreign_community_id']}",
                "Xml": xml
            }

            # Call the outgoing
            outgoing = self.outgoing.plain_http[OUTGOING_POST]
            outgoing_response = outgoing.conn.post(self.cid, data=data, headers=headers.get())
            response = json.loads(Converter(outgoing_response.text).xml_to_json())
            if response[RESMAN][STATUS] != "Success":
                self.response.status_code = HTTP_BAD_REQUEST_CODE
                error = response[RESMAN][ERROR_DESCRIPTION]
                self.logger.error(f"Resman error response: {error}")
                response = {
                    "data": [],
                    "errors": [{"message": f"{error}"}],
                }
                self.response.payload = response
                return response

            # Success case
            data_response = {
                "data": [response[RESMAN][RESPONSE]],
                "partnerId":integration_partner_id,
                "errors": []
            }
          
            self.response.payload = self.get_response(response[RESMAN][RESPONSE], available_times, tour_schedule, tour_scheduled_id, tour_requested, tour_error, "")
            return data_response

        except Exception as e:
            self.logger.error(f"{HTTP_SERVER_ERROR_MSJ}: {e}")
            self.response.status_code = 504
            data_response = {
                "data": [],
                "errors": [{"message": f"{HTTP_SERVER_ERROR_MSJ}"}],
            }
            self.response.payload = data_response
            return data_response

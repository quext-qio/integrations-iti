import json
import requests
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.shared.config import config
from utils.shared.payload_handler import PayladHandler
from services.shared.quext_tour_service import QuextTourService
from constants.resman_constants import *
from Converter import Converter
from utils.service_response import ServiceResponse


class ResManService(ServiceInterface):

    def get_data(self, body, ips, logger):

        logger.info(f"Getting data from ResMan")
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
                "PropertyID": f"{ips['params']['foreign_community_id']}"
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'request': 'application/xml'
            }
            url = "https://api.myresman.com/Leasing/GetProspectSources"
            outgoing_prospect_source = requests.post(
                url, headers=headers, data=resman_params)

            prospects_list = json.loads(outgoing_prospect_source.text)
            prospectSourceId = ""
            tour_comment = ""
            first_contact = True
            # Seach the prospectSourceID
            for prospect in prospects_list["ProspectSources"]:
                if prospect["Name"] == "Quext":
                    prospectSourceId = prospect["ID"]

            if "tourScheduleData" in body:
                logger.info(f"tourScheduleData is available in the payload")
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

            # If the prospect is completely new
            # Create body for resman
            tour_information = {
                "availableTimes": available_times,
                "tourScheduledID": tour_scheduled_id,
                "tourRequested": appointment_date,
                "tourSchedule": True if tour_scheduled_id else False,
                "tourError": tour_error
            }
            event = {
                "Source": body["source"],
                "EventType": "WalkIn",
                "FirstContact": first_contact,
                "EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "TransactionSourceid": prospectSourceId,
                "UnitID": "",
                "Comments": tour_comment
            }
            event = PayladHandler().create_events(event, ips)
            xml = Converter(PayladHandler().builder_payload(
                body, event)).json_to_xml()
            resman_params.update({"Xml": xml})

            # Call the outgoing
            response, errors = self.save_prospect(xml, ips, logger)
            # If the response is not success, start testing all scenarios
            if len(errors) != 0:
                logger.warn(f"Error while saving prospect: {errors}")

                del resman_params["Xml"]
                resman_params.update({"email": body["guest"]["email"]})
                new_event = event
                logger.info(f"Searching Prospect with Email")
                # Consult if prospect exists by email
                get_response = self.search_prospects(resman_params, logger)

                # QIN-5468: If the email was not found, search with phone
                if get_response[LEADMANAGEMENT][PROSPECTS] == None:
                    logger.info(f"Email address does not exists, searching with phone number")
                    del resman_params["email"]
                    resman_params.update({"phone": body["guest"]["phone"]})

                    # Consult if prospect exists by email
                    get_response = self.search_prospects(resman_params, logger)

                # If the prospect was found, build a new xml add the new event to the found prospect
                if get_response[LEADMANAGEMENT][PROSPECTS] != None:
                    new_xml = get_response
                    data_to_update = new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                    comment = new_event['Comments'] if "Comments" in new_event else ""
                    event_to_modify = data_to_update
                    new_event = new_event["Event"]
                    # order events list By date

                    if type(data_to_update) == list:
                        data_to_update.sort(key=lambda x: datetime.strptime(
                            x['@EventDate'][0:x['@EventDate'].index("T")], '%Y-%m-%d'), reverse=True)
                        event_to_modify = data_to_update[0]
                    # Verify if event comments already contains tour information
                    is_new, event_modified, message = self.verify_event_fields(
                        event_to_modify, new_event["@EventDate"], event_to_modify["Comments"], tour_comment)
                    # Compare 2 phone numbers
                    if is_new:

                        new_phone_number = body["guest"].get("phone")
                        phone_number_found = get_response["LeadManagement"][
                            "Prospects"]["Prospect"]["Customers"]["Customer"].get("Phone")

                        new_email = body["guest"]["email"]
                        email_found = get_response["LeadManagement"][
                            "Prospects"]["Prospect"]["Customers"]["Customer"]["Email"]
                        new_event.update({"FirstContact": "false"})

                        if new_phone_number != phone_number_found:
                            # add phone number to event, also update
                            comment += f"Phone: {new_phone_number} "

                        if new_email != email_found:
                            # add email address to event, also update
                            comment += f"Email: {new_email} "

                        new_event.update({"Comments": comment})
                        new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"] = {'PhoneNumber': new_phone_number}
                        new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Email"] = new_email

                        # If the Events in the result is a list is going to append the new event
                        if type(data_to_update) == list:
                            new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"] = [new_event]
                        # if not, transform the dict to List (adding the new event)
                        else:
                            new_list = [data_to_update, new_event]
                            new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"] = new_list
                    else:
                        tour_error = message
                        new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"].update(
                            {"Event": event_modified})
                        available_times = [] if message != "" else available_times

                    xml = Converter(new_xml).json_to_xml()
                    prospect_updated, errors = self.save_prospect(xml, ips, logger)
                    if len(errors) != 0:
                        logger.warn(f"Error while saving the prospect data: {errors}")
                        new_xml["LeadManagement"]["Prospects"]["Prospect"]["Customers"]["Customer"]["Phone"] = ""

                        event = new_xml["LeadManagement"]["Prospects"]["Prospect"]["Events"]["Event"]
                        event = event[0] if type(event) == list else event
                        event.update(
                            {"Comments": event['Comments'] if "Comments" in new_event else "" + tour_comment})
                        xml = Converter(new_xml).json_to_xml()
                        response, errors = self.save_prospect(xml, ips, logger)
                        response = errors
                    else:
                        response = prospect_updated

            # Success case
            tour_information = {
                "availableTimes": available_times,
                "tourScheduledID": tour_scheduled_id,
                "tourRequested": appointment_date,
                "tourSchedule": True if tour_scheduled_id else False,
                "tourError": tour_error
            }

            prospect_id = response["ResMan"]["Response"]["LeadManagement"]["Prospects"][
                "Prospect"]["Customers"]["Customer"]["Identification"][0]["@IDValue"]

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

        except Exception as e:
            logger.error(f"Error from Resman GuestCard service{e}")
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

    def verify_event_fields(self, json_to_verify, date, actual_comment, tour_comment):
        # Ask if EventDate is today date, if so, update the comment with tour info, if not, create a new event
        message = ""
        event = json_to_verify
        is_new = False
        actual_comment = actual_comment if actual_comment != None else ""

        if str(datetime.utcnow().strftime("%Y-%m-%d")) in date:
            if actual_comment != "" and "--TOURS--" in actual_comment:
                is_new = False
                message = "Guest Card and Scheduled a Tour have already been submitted"
            else:
                is_new = True
                event.update({"Comments": tour_comment})

        else:
            is_new = True

        return is_new, event, message

    def search_prospects(self, payload, logger):

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
                response = json.loads(Converter(response.text).xml_to_json())
                return response[RESMAN][RESPONSE]

            else:
                logger.error(
                    f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making the request: {e}")

    def save_prospect(self, payload, ips, logger):
        integration_partner_id = config['Integration_partner_id']
        api_key = config['ApiKey']
        account_id = config["resman_account_id"]
        try:
            # Create body for resman

            data = {
                "IntegrationPartnerID": f"{integration_partner_id}",
                "APIKey": f"{api_key}",
                "AccountID": f"{account_id}",
                "PropertyID": f"{ips['params']['foreign_community_id']}",
                "Xml": payload
            }

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'request': 'application/xml'
            }
            url = "https://api.myresman.com/MITS/PostLeadManagement4_0"
            outgoing_save_prospect = requests.post(
                url, headers=headers, data=data)
            response = json.loads(
                Converter(outgoing_save_prospect.text).xml_to_json())

            if response[RESMAN][STATUS] != "Success":
                error = response[RESMAN][ERROR_DESCRIPTION]
                errors = [{"message": error}]
                logger.warning(
                    f"Unhandled Error in RESMAN Guestcard 295: {error}")
                return [], errors

            # Success case
            return response, []

        except Exception as e:
            logger.warn(f"Unhandled Error in RESMAN Guestcard 306: {e}")
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

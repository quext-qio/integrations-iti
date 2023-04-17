import json
from datetime import datetime
from urllib.parse import urlencode

from CalendarServiceShared.Controller.CalendarGatewayController import CalendarGatewayController
from ExceptionHandling.Model.Exceptions import GatewayError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode, ErrorConstants
from GuestCardShared.Utils.GuestCardResponse import GuestCardResponse, GuestCardInformation, TourInformation
from LocationShared.Model.LocationResponse import Location
from ResmanShared.Model.ResmanResponse import CurrentResidentResponse, LeaseResponse, ProspectResponse
from ResmanShared.Utilities.ResmanConstants import ResmanConstants
from ResmanShared.Utilities.ResmanMapper import ResmanMapper
from ResmanShared.Utilities.ResmanUtilities import ResmanUnitResponse
from TourShared.Model.Data_Model import TourAvailabilityData
from Utils.Converter import Converter
from VendorShared.Controller.VendorGatewayController import VendorGatewayController
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants, VendorLayout, get_vendor_layout, \
    get_source_and_agent
from VendorShared.Utilities.Utils import trim_utc_date
from Utils import CustomLogger

logging = CustomLogger.logger

class ResmanGatewayController(VendorGatewayController):
    """
    ResmanGatewayController class for handling Resman related communication and data transformations
    """

    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Get Unit and Price information
        """
        logging.info("Getting unit availablity from ResMan")
        outgoing_platform_request = service_request.outgoing.plain_http[ResmanConstants.RESMAN_EXTERNAL]
        _params = self.__get_parameters(ResmanConstants.AVAILABILITY_PRICING_INTERFACE,
                                        ResmanConstants.AVAILABILITY_PRICING_METHOD)

        # Preparing payload
        _headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        service_payload = service_request.request.payload

        service_request.auth.add_property(ResmanConstants.PROPERTY_ID,
                                          service_request.auth.pop_property(ResmanConstants.FOREIGN_COMMUNITY_ID))

        _body = urlencode(
            {key: value for key, value in vars(service_request.auth).items() if key != ResmanConstants.PLATFORM})

        # Initiating ResMan service call
        response = ResmanGateway().call_resman(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                               body=_body, params=_params, headers=_headers,
                                               content_type=ResmanConstants.CONTENTTYPE)
        unit_response_object = ResmanUnitResponse()
        unit_available = unit_response_object.generate_availability_response(response, service_payload)
        return unit_available

    def book_tour_appointment(self, service_request: ServiceRequest, appointmentData=None):
        """
        Creating Tour
        """
        logging.debug("Creating Tour Schedule")
        response = CalendarGatewayController().post_appointment(service_request)
        return response

    def get_tour_availabilities(self, service_request: ServiceRequest,
                                tour_availability_data: TourAvailabilityData = None):
        """
        Returns the Tour Availability Datetime from the Quext Calendar Service
        """
        logging.debug("Fetching Tour Availability")
        response = CalendarGatewayController().get_tour_availability(service_request, tour_availability_data)
        return response

    def get_residents(self, service_request: ServiceRequest):
        """
        Get residents information
        """
        logging.debug("Getting Residents from ResMan")
        outgoing_platform_request = service_request.outgoing.plain_http[ResmanConstants.RESMAN_EXTERNAL]
        _params = self.__get_parameters(ResmanConstants.RESIDENTS_INTERFACE, ResmanConstants.RESIDENTS_METHOD)
        # Preparing payload
        _headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        service_request.auth.add_property(ResmanConstants.PROPERTY_ID,
                                          service_request.auth.pop_property(ResmanConstants.FOREIGN_COMMUNITY_ID))
        _body = urlencode(
            {key: value for key, value in vars(service_request.auth).items() if key != ResmanConstants.PLATFORM})

        # Initiating ResMan service call
        response = ResmanGateway().call_resman(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                               body=_body, params=_params, headers=_headers)
        search_resident_response = CurrentResidentResponse(**response)
        resman_mapper = ResmanMapper(service_request)
        resman_response = resman_mapper.residents_mapper(search_resident_response)
        return resman_response

    def get_leases(self, service_request: ServiceRequest):
        """
        Get leasing residents information
        """
        logging.debug("Getting Leasing Residents from ResMan")
        outgoing_platform_request = service_request.outgoing.plain_http[ResmanConstants.RESMAN_EXTERNAL]
        _params = self.__get_parameters(ResmanConstants.LEASING_INTERFACE, ResmanConstants.LEASING_METHOD)

        # Preparing payload
        _headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        service_request.auth.add_property(ResmanConstants.PROPERTY_ID,
                                          service_request.auth.pop_property(ResmanConstants.FOREIGN_COMMUNITY_ID))
        service_request.auth.add_property(ResmanConstants.INCLEASEHISTORY, True)
        _body = urlencode(
            {key: value for key, value in vars(service_request.auth).items() if key != ResmanConstants.PLATFORM})

        # Initiating ResMan service call
        response = ResmanGateway().call_resman(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                               body=_body, params=_params, headers=_headers)
        person_response = LeaseResponse(**response)
        resman_mapper = ResmanMapper(service_request)
        resman_response = resman_mapper.leases_mapper(person_response)
        return resman_response

    def get_locations(self, service_request: ServiceRequest):
        """
        Returns the Locations data from resman

        Parameters
        ----------
        service_request : Zato Request Object
        """
        # using constants for headers gives empty response, so headers are hardcoded in this function
        _headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
        outgoing_ips_channel = service_request.outgoing.plain_http[ResmanConstants.RESMAN_EXTERNAL]
        _params = self.__get_parameters(ResmanConstants.UNITS_INTERFACE, ResmanConstants.UNITS_METHOD)
        service_request.auth.add_property(ResmanConstants.PROPERTY_ID,
                                          service_request.auth.pop_property(ResmanConstants.FOREIGN_COMMUNITY_ID))
        _body = urlencode({key: value for key, value in vars(service_request.auth).items()
                           if key != ResmanConstants.PLATFORM})
        # logging the URL Encoded API Configuration
        logging.info("API Config URL Encoding Success")
        response = ResmanGateway().call_resman(conn=outgoing_ips_channel.conn, cid=service_request.cid,
                                               body=_body, params=_params, headers=_headers)
        # logging the UNITS Endpoint Response From Resman
        location_list = [Location(**i) for i in response[ResmanConstants.UNITS]]
        resman_mapper = ResmanMapper(service_request)
        resman_response = resman_mapper.location_mapper(location_list)
        return resman_response

    def __get_parameters(self, interface: str = "", method: str = ""):
        """
        Returns the URL parameters

        Parameters
        ----------
        method : URL Method (properties , customers , etc)
        """
        params = {
            "interface": str(interface),
            "method": str(method)
        }
        return params

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Get guest card information
        """
        logging.info("Creating guest card for Resman")
        _headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        _params = self.__get_parameters(ResmanConstants.LEASING_INTERFACE, ResmanConstants.GETPROSPECTSOURCES)
        outgoing_prospect_source = service_request.outgoing.plain_http[ResmanConstants.RESMAN_EXTERNAL]
        service_request.auth.add_property(ResmanConstants.PROPERTY_ID,
                                          service_request.auth.pop_property(ResmanConstants.FOREIGN_COMMUNITY_ID))
        not_req_auth_field = ResmanConstants.PLATFORM, ResmanConstants.DH, ResmanConstants.WS, \
            ResmanConstants.FOREIGNCUSTOMERID, ResmanConstants.SOURCE
        _body = urlencode(
            {key: value for key, value in vars(service_request.auth).items() if key not in not_req_auth_field})

        # Getting Prospect Source from ResMan
        logging.info("Getting Prospect Source from ResMan")
        response = ResmanGateway().call_resman(conn=outgoing_prospect_source.conn, cid=service_request.cid,
                                               body=_body, headers=_headers, params=_params)
        logging.debug(response)
        prospect_response = ProspectResponse(**response)
        prospectSourceId = ""
        for prospect in prospect_response.ProspectSources:
            if prospect.Name == ResmanConstants.QUEXT:
                prospectSourceId = prospect.ID
                logging.info("Prospect Source Id :" + prospectSourceId)

        # Create Tour Scheduling if present
        quext_calendar_comment = ''
        tourscheduled_id = ''
        if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
            response = CalendarGatewayController().post_appointment(service_request=service_request)
            if response.get(ResmanConstants.DATA):
                quext_calendar_comment = response[ResmanConstants.DATA][ResmanConstants.COMMENTS]
                tourscheduled_id = response[ResmanConstants.DATA][ResmanConstants.APPOINTMENT_ID]
            else:
                output = GuestCardResponse()
                output.guestCardInformation = GuestCardInformation()
                logging.info("Available list: {}".format(response))
                output.guestCardInformation.firstName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.FIRSTNAME]
                output.guestCardInformation.lastName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.LASTNAME]
                output.tourInformation = TourInformation()
                output.tourInformation.availableTimes = response.get(ResmanConstants.AVAILABLETIMES)
                output.tourInformation.tourRequested = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
                output.tourInformation.tourSchedule = False
                output.tourInformation.tourError = response.get(ResmanConstants.ERROR)
                logging.info("Error response: {}".format(vars(output)))
                return output

        # Create Guest Card for ResMan
        payload = self._prepare_guestcard_payload(service_request, prospectSourceId, quext_calendar_comment)
        # Calling ResMan for creating Guest Card
        logging.info("Calling ResMan for creating Guest Card")
        _params = self.__get_parameters(ResmanConstants.MITS, ResmanConstants.POST_LEAD_MANAGEMENT)
        post_lead_management_outgoing = service_request.outgoing.plain_http[ResmanConstants.POST_LEAD_MANAGEMENT_REST]
        outgoing_response = post_lead_management_outgoing.conn.post(service_request.cid, data=payload, headers=_headers)
        response = json.loads(Converter(outgoing_response.text).xml_to_json())
        logging.info("ResMan Guest Card response : {}".format(response))

        # If the guest card creation is success
        if response[ResmanConstants.SOURCESYSTEM][ResmanConstants.STATUS] == ResmanConstants.SUCCESS:
            logging.info("Preparing output")
            output = self._generate_guestcard_response(response, VendorConstants.NEW, VendorConstants.INSERT, service_request, tourscheduled_id)
            return output

        # if response is not success
        if response[ResmanConstants.SOURCESYSTEM][ResmanConstants.STATUS] != ResmanConstants.SUCCESS:
            # Case #1, if email and phone already exist
            # Consult if prospect exists by email
            auth = service_request.auth
            request = {
                ResmanConstants.INTEGRATION_PARTNER_ID: auth.get_property(ResmanConstants.INTEGRATION_PARTNER_ID),
                ResmanConstants.API_KEY: auth.get_property(ResmanConstants.API_KEY),
                ResmanConstants.ACCOUNT_ID: auth.get_property(ResmanConstants.ACCOUNT_ID),
                ResmanConstants.PROPERTY_ID: auth.get_property(ResmanConstants.PROPERTY_ID)
            }
            body_search = {"email": response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.EMAIL]}
            body_search.update(request)
            logging.info("search prospect with email".format(body_search))
            search_prospect_response = self.search_prospects(data=body_search, service_request=service_request, headers=_headers)

            # If the email was found, build a new xml add the new event to the found prospect
            if search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][ResmanConstants.LEAD_MANAGEMENT][
                ResmanConstants.PROSPECTS] != None:
                logging.info(search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                                  ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS])
                new_event = \
                    response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][ResmanConstants.LEAD_MANAGEMENT][
                        ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.EVENTS][
                        ResmanConstants.EVENT]
                new_xml = search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE]
                data_to_update = \
                    new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.EVENTS][ResmanConstants.EVENT]

                # Compare 2 phone numbers
                new_phone_number = \
                    response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][ResmanConstants.LEAD_MANAGEMENT][
                        ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.CUSTOMERS][
                        ResmanConstants.CUSTOMER].get(ResmanConstants.PHONE) and \
                        response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][ResmanConstants.LEAD_MANAGEMENT][
                        ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.CUSTOMERS][
                        ResmanConstants.CUSTOMER][ResmanConstants.PHONE] or ''
                phone_number_found = \
                    new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER].get(ResmanConstants.PHONE) \
                    and new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.PHONE] or ''
                new_event.update({ResmanConstants.FIRST_CONTACT: "false"})
                new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                    ResmanConstants.CUSTOMER_PREFERENCES] = \
                response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                    ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                    ResmanConstants.CUSTOMER_PREFERENCES]
                if new_phone_number != phone_number_found:
                    logging.debug("compare phone number")
                    # add phone number to event, also update
                    comment = new_event[ResmanConstants.COMMENTS] if ResmanConstants.COMMENTS in new_event else ""
                    if comment != "":
                        comment += str({ResmanConstants.PHONE: new_phone_number})
                    else:
                        comment += str({ResmanConstants.PHONE: new_phone_number})
                    new_event.update({ResmanConstants.COMMENTS: comment})
                    new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.PHONE] = new_phone_number

                # If the Events in the result is a list is going to append the new event
                if type(data_to_update) == list:
                    data_to_update.append(new_event)
                # if not, transform the dict to List (adding the new event)
                else:
                    new_list = [data_to_update, new_event]
                    new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.EVENTS][ResmanConstants.EVENT] = new_list

                # Payload to update
                xml = Converter(json.dumps(new_xml)).json_to_xml()
                update_payload = {ResmanConstants.XML: xml}
                update_payload.update(request)
                prospect_updated = self.update_prospect(update_payload, service_request, headers=_headers)
                output = self._generate_guestcard_response(prospect_updated, VendorConstants.EXIST, VendorConstants.UPDATE, service_request, tourscheduled_id)
                return output
            else:
                # check if phone number exists
                phone = {"phone": response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                    ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                    ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.PHONE][
                    ResmanConstants.PHONENUMBER]}
                phone.update(request)
                logging.info("search prospect with phone_number".format(phone))
                search_prospect_response = self.search_prospects(data=phone, service_request=service_request, headers=_headers)

                if search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                    ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS] != None:
                    logging.info(search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                                     ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS])
                    new_event = \
                        response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                            ResmanConstants.LEAD_MANAGEMENT][
                            ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.EVENTS][
                            ResmanConstants.EVENT]
                    new_xml = search_prospect_response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE]
                    exiting_events = \
                        new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                            ResmanConstants.EVENTS][ResmanConstants.EVENT]
                    # Compare 2 emails
                    new_email = \
                        response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                            ResmanConstants.LEAD_MANAGEMENT][
                            ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.CUSTOMERS][
                            ResmanConstants.CUSTOMER][ResmanConstants.EMAIL]
                    email_found = \
                        new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                            ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.EMAIL]
                    new_event.update({ResmanConstants.FIRST_CONTACT: "false"})
                    if new_email != email_found:
                        logging.info("compare email")
                        # add phone number to event, also update
                        comment = new_event[ResmanConstants.COMMENTS] if ResmanConstants.COMMENTS in new_event else ""
                        if comment != "":
                            comment += str({ResmanConstants.EMAIL: new_email})
                        else:
                            comment += str({ResmanConstants.EMAIL: new_email})
                        new_event.update({ResmanConstants.COMMENTS: comment})
                        new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                            ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.EMAIL] = new_email
                    # If the Events in the result is a list is going to append the new event
                    if type(exiting_events) == list:
                        exiting_events.append(new_event)
                    # if not, transform the dict to List (adding the new event)
                    else:
                        new_list = [exiting_events, new_event]
                        new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                            ResmanConstants.EVENTS][ResmanConstants.EVENT] = new_list
                    new_xml[ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                        ResmanConstants.CUSTOMER_PREFERENCES] = response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                        ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][ResmanConstants.CUSTOMER_PREFERENCES]
                    # Payload to update
                    xml = Converter(json.dumps(new_xml)).json_to_xml()
                    update_payload = {ResmanConstants.XML: xml}
                    update_payload.update(request)
                    prospect_updated = self.update_prospect(update_payload, service_request, headers=_headers)
                    output = self._generate_guestcard_response(prospect_updated, VendorConstants.EXIST, VendorConstants.UPDATE, service_request, tourscheduled_id)
                    return output
                else:
                    return {}

    def _prepare_guestcard_payload(self, service_request: ServiceRequest, prospectSourceId, quext_calendar_comment):
        """
        Preparing payload for guestcard and Tour schedule if applicable
        """
        logging.debug("Prepare GuestCard: Resman")
        prospect = service_request.request.payload.get(VendorConstants.PROSPECT) and \
                   service_request.request.payload[VendorConstants.PROSPECT] or None

        customer_preference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE) or {}
        desired_bedroom = ''
        desired_rent = ''
        lease_term_months = ''
        move_in_date = ''
        floorplan = ''

        if customer_preference:
            desired_bedroom = get_vendor_layout(VendorLayout.RESMAN,
                                                customer_preference.get(VendorConstants.DESIRED_BEDROOM)
                                                and customer_preference[VendorConstants.DESIRED_BEDROOM])

            desired_bathroom = customer_preference.get(VendorConstants.DESIRED_BATHROOM) \
                               and customer_preference[VendorConstants.DESIRED_BATHROOM] or []

            desired_rent = customer_preference.get(VendorConstants.DESIRED_RENT) \
                           and customer_preference[VendorConstants.DESIRED_RENT] or None

            lease_term_months = customer_preference.get(VendorConstants.LEASE_TERM_MONTHS) \
                                and customer_preference[VendorConstants.LEASE_TERM_MONTHS] or None

            move_in_date = customer_preference.get(VendorConstants.MOVE_IN_DATE) \
                           and customer_preference[VendorConstants.MOVE_IN_DATE] or None

            move_in_date = trim_utc_date(move_in_date)

            floorplan = []
            for beds in desired_bedroom:
                floorplan.append(str(beds) + ResmanConstants.B)
                for baths in desired_bathroom:
                    floorplan.pop(floorplan.index(str(beds) + ResmanConstants.B))
                    floorplan.append(str(beds) + ResmanConstants.B + str(baths) + ResmanConstants.B.lower())
            floorplan = ','.join(floorplan)

        phone_number = prospect.get(VendorConstants.PHONE) \
                        and prospect[VendorConstants.PHONE] or ''
        formatted_number = phone_number and "({}{}{}) {}{}{}-{}{}{}{}".format(*phone_number) or ''
        comments = service_request.guest_card_comment

        source, agentId = get_source_and_agent(service_request.auth.get_property('source'), service_request)
        xml = {
            "xml": {
                "LeadManagement": {
                    "Prospects": {
                        "Prospect": {
                            "Customers": {
                                "Customer": {
                                    "@Type": "prospect",
                                    "Name": {
                                        "FirstName": prospect[VendorConstants.FIRSTNAME],
                                        "MiddleName": "",
                                        "LastName": prospect[VendorConstants.LASTNAME]
                                    },
                                    "Phone": {
                                        "PhoneNumber": formatted_number
                                    },
                                    "Email": prospect[VendorConstants.EMAIL] or '',
                                }
                            },
                            "CustomerPreferences": {
                                "TargetMoveInDate": move_in_date,
                                "DesiredFloorplan": floorplan,
                                "DesiredRent": {"@Exact": desired_rent},
                                "DesiredNumBedrooms": {"@Exact": desired_bedroom},
                                "DesiredLeaseTerms": lease_term_months,
                                "Comments": comments},
                            "Events": {
                                "Event": {
                                    "@EventType": ResmanConstants.WALKIN,
                                    "@EventDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                                    "Agent": {
                                        "AgentID": {
                                            "@IDValue": agentId
                                        },
                                        "AgentName": {
                                            "FirstName": source,
                                            "LastName": ResmanConstants.QUEXT
                                        }
                                    },
                                    "FirstContact": ResmanConstants.TRUE,
                                    "TransactionSource": prospectSourceId,
                                    "Comments": comments + quext_calendar_comment
                                }
                            }
                        }
                    }
                }
            }
        }

        json_to_convert_xml = xml[ResmanConstants.XML.lower()]
        xml = Converter(json.dumps(json_to_convert_xml)).json_to_xml()
        logging.info("Prepared resMan GuestCard Payload : {}".format(xml))
        auth = service_request.auth
        data = {
            ResmanConstants.INTEGRATION_PARTNER_ID: auth.get_property(ResmanConstants.INTEGRATION_PARTNER_ID),
            ResmanConstants.API_KEY: auth.get_property(ResmanConstants.API_KEY),
            ResmanConstants.ACCOUNT_ID: auth.get_property(ResmanConstants.ACCOUNT_ID),
            ResmanConstants.PROPERTY_ID: auth.get_property(ResmanConstants.PROPERTY_ID),
            ResmanConstants.XML: xml
        }
        return data

    def search_prospects(self, data, service_request: ServiceRequest, headers):
        """
        Search the prospects with given data

        Params:
        -------
        data: dict - Contains search request data
        service_request: ServiceRequest - ServiceRequest object contains input request data from client
        headers: dict - Header information used for sending request to ResMan

        Return:
        -------
        Json object from ResMan response
        """
        logging.info('Searching Prospects')
        outgoing = service_request.outgoing.plain_http[ResmanConstants.SEARCH_PROSPECT]
        outgoing_response = outgoing.conn.post(service_request.cid, data=data, headers=headers)
        response = json.loads(Converter(outgoing_response.text).xml_to_json())
        logging.info("Search Prospect response : {}".format(response))
        return response

    def update_prospect(self, data, service_request: ServiceRequest, headers):
        """
        Call resman guestcard with updated prospect
        """
        logging.info('Update prospect')
        outgoing = service_request.outgoing.plain_http[ResmanConstants.POST_LEAD_MANAGEMENT_REST]
        outgoing_response = outgoing.conn.post(service_request.cid, data=data, headers=headers)
        response = json.loads(Converter(outgoing_response.text).xml_to_json())
        logging.info(response)
        return response
    
    def _generate_guestcard_response(self, response, status, action, service_request, tourscheduled_id):
        """
        Generate guestcard and tour schedule response
        """
        logging.info("generate guestcard response")
        output = GuestCardResponse()
        output.guestCardInformation = GuestCardInformation()
        output.guestCardInformation.guestCardId = \
            response[ResmanConstants.SOURCESYSTEM][ResmanConstants.RESPONSE][
                ResmanConstants.LEAD_MANAGEMENT][ResmanConstants.PROSPECTS][ResmanConstants.PROSPECT][
                ResmanConstants.CUSTOMERS][ResmanConstants.CUSTOMER][ResmanConstants.IDENTIFICATION][
                0][ResmanConstants.IDVALUE]
        output.guestCardInformation.result = response[ResmanConstants.SOURCESYSTEM][ResmanConstants.STATUS]
        output.guestCardInformation.firstName = service_request.request.payload[VendorConstants.PROSPECT
                                                ][VendorConstants.FIRSTNAME]
        output.guestCardInformation.lastName = service_request.request.payload[VendorConstants.PROSPECT
                                                ][VendorConstants.LASTNAME]
        output.guestCardInformation.status = status
        output.guestCardInformation.action = action
        if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
            output.tourInformation = TourInformation()
            output.tourInformation.tourScheduledID = tourscheduled_id
            output.tourInformation.tourRequested =  \
                                service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA) \
                                and service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA
                                ][VendorConstants.START] or None
            output.tourInformation.tourSchedule = tourscheduled_id and True or False
        else:
            output.__delattr__('tourInformation')
        logging.info(vars(output))
        return output

class ResmanGateway:
    """
    ResManGateway to connect ResMan service to exchange the data
    """

    def call_resman(self, conn, cid, body, params, headers, content_type=None):
        """
        Implements All ResMan API Endpoint and returns the response

        Parameters
        ----------
        conn : Outgoing Connection Object
        body : Api request data
        params : query params
        headers : Api Headers
        cid : Zato Connection ID
        content_type : Content type

        Returns
        --------
        dict
        """
        logging.info("Inside call resman ")
        try:
            # Connecting ResMan
            response = conn.post(cid, data=body, params=params, headers=headers)
        except Exception as e:
            logging.exception(e.__str__())
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, VendorConstants.BAD_REQUEST)

        # Preparing response object
        if content_type == ResmanConstants.CONTENTTYPE:
            response_content = response.text
        else:
            response_content = response.json()

        # Checking the status of the response
        if response.status_code > 300:
            logging.debug("Invalid Response : {}".format(response))
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, response.status_code)
        return response_content

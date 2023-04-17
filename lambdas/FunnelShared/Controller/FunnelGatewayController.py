import logging
import os
from datetime import datetime
from enum import Enum
from bunch import bunchify
import json

from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode, ErrorConstants
from FunnelShared.Utilities.FunnelConstants import FunnelConstants
from TourShared.Model.Data_Model import TourAvailabilityData, Data
from Utils.Headers import Headers
from VendorShared.Controller.VendorGatewayController import VendorGatewayController
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants, VendorLayout, get_vendor_layout
from DataPushPullShared.Utilities.DataController import  DataValidation, Schema
from GuestCardShared.Utils.GuestCardResponse import  GuestCardResponse, GuestCardInformation, TourInformation
from VendorShared.Utilities.Utils import trim_utc_date
from DataPushPullShared.Utilities.Convert import Convert




class FunnelGatewayController(VendorGatewayController):

    def get_residents(self, service_request: ServiceRequest):
        pass

    def get_leases(self, service_request: ServiceRequest):
        pass

    def get_locations(self, service_request: ServiceRequest):
        pass

    def get_unit_availability(self, service_request: ServiceRequest):
        pass

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Tour Schedule Creation For Funnel
        Guest Card Creation Handled Making The Appointment date as today - TBD
        """
        # Validating Payload Guest Card Schema
        self.__validate(servicerequest=service_request, schema=Schema.GUEST_CARDS)

        #Get the source details using the apikey
        source_details = self.__get_wsdl(service_request)

        is_production = True if os.environ['PRODUCTION'] == "True" else False
        _headers = self.__get_auth_header()
        body = self.__get_from_payload_for_guestcards(service_request, source_details)

        tour_response = {}
        #Framing the Funnel POST Payload for schedule tour
        if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
            _params = {
            "group_id": service_request.auth.get_property(
                FunnelConstants.FOREIGN_COMMUNITY_ID) if is_production else 778,
            }
            outgoing_platform_request = service_request.outgoing.plain_http[FunnelConstants.FUNNEL_OUTGOING_POST]
            outgoing_funnel_response = FunnelGateway().call_funnel(conn=outgoing_platform_request.conn, cid=service_request.cid, body=body, params=_params,
                                                   headers=_headers, method="POST")
            logging.debug("outgoing funnel response for GuestCard/TourSchedule  %s" %outgoing_funnel_response)
            if FunnelConstants.DATA in outgoing_funnel_response:
                # Success response of funnel
                funnel_appointment = outgoing_funnel_response[FunnelConstants.DATA][FunnelConstants.APPOINTMENT]
                funnel_response = {
                    "guestCardId": funnel_appointment[FunnelConstants.ID],
                    "result": FunnelConstants.SUCCESS
                }
                tour_response = {
                    "tourScheduledID": funnel_appointment[FunnelConstants.ID],
                    "tourSchedule": True
                }
            else:
                tour_availability_data = TourAvailabilityData()
                tour_availability_data.fromDate = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START].split('T')[0]
                tour_availability_data.toDate = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START].split('T')[0]
                tour_availabilities = self.get_tour_availabilities(service_request, tour_availability_data)
                utc_date_list = Convert.get_utc(tour_availabilities.availableTimes, 'UTC')
                logging.debug("available_times of funnel %s" %utc_date_list)
                funnel_response = {
                                    "result": FunnelConstants.FAILURE
                                  }
                tour_response = {
                                    "tourSchedule": False,
                                    "tourError": outgoing_funnel_response[FunnelConstants.ERRORS][FunnelConstants.APPOINTMENT],
                                    "availableTimes": utc_date_list
                                 }

                logging.debug("available_times of tour_response %s" %tour_response)
        else:
            outgoing_platform_request = service_request.outgoing.plain_http[FunnelConstants.FUNNEL_OUTGOING_GC_ONLY]
            body[FunnelConstants.CLIENT].update({
                        "group": service_request.auth.get_property(
                        FunnelConstants.FOREIGN_COMMUNITY_ID) if is_production else 778,
                         })
            outgoing_funnel_response = FunnelGateway().call_funnel(conn=outgoing_platform_request.conn, cid=service_request.cid, body=body,
                                                   headers=_headers, params={}, method="POST")
            logging.debug("outgoing funnel response for GC  %s" %outgoing_funnel_response)
            funnel_client = outgoing_funnel_response[FunnelConstants.DATA][FunnelConstants.CLIENT]
            funnel_response = {
                                "result" : FunnelConstants.SUCCESS,
                                "guestCardId": funnel_client[FunnelConstants.ID]
                              }
        #Framing return response for the endpoint
        res = GuestCardResponse()
        if funnel_response:
            res.guestCardInformation = GuestCardInformation(**funnel_response)
            res.guestCardInformation.firstName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.FIRSTNAME]
            res.guestCardInformation.lastName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.LASTNAME]
            if FunnelConstants.RESULT in funnel_response:
                res.guestCardInformation.result = funnel_response[FunnelConstants.RESULT]
            if FunnelConstants.GCID in funnel_response:
                res.guestCardInformation.guestCardId = funnel_response[FunnelConstants.GCID]
            res.guestCardInformation.action = FunnelConstants.INSERT
            res.guestCardInformation.status = FunnelConstants.STATUS
            if tour_response:
                res.tourInformation = TourInformation(**tour_response)
                if VendorConstants.TOUR_SCHEDULE_DATA in service_request.request.payload:
                    res.tourInformation.tourRequested = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
            return res
        res.guestCardInformation = GuestCardInformation(FirstName=service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.FIRSTNAME] \
                                ,LastName=service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.LASTNAME])
        return res


    def get_tour_availabilities(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):
        is_production = True if os.environ['PRODUCTION'] == "True" else False
        _params = {
            "group_id": service_request.auth.get_property(
                FunnelConstants.FOREIGN_COMMUNITY_ID) if is_production else 778,
            "from_date": tour_availability_data.fromDate,
            "to_date": tour_availability_data.toDate if tour_availability_data.toDate is not None else ""
        }
        _headers = self.__get_auth_header()
        outgoing_platform_request = service_request.outgoing.plain_http[FunnelConstants.FUNNEL_OUTGOING_GET]
        response = FunnelGateway().call_funnel(conn=outgoing_platform_request.conn, cid=service_request.cid, body=None, params=_params,
                                               headers=_headers, method="GET")
        # If exist an error from funnel
        if not "available_times" in response:
            logging.error(f"Error from Funnel: {response['errors']}")
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, response['errors'], VendorConstants.BAD_REQUEST)

        # If empty response, return an error
        data = response["available_times"]
        if len(data) == 0:
            logging.error("Funnel services is not responding or has provided an empty payload.")
            raise GatewayError(ErrorCode.ERROR_HTTP_0001,
                               {"message": "Please contact the leasing office by phone to schedule a tour."},
                               VendorConstants.CONFLICT)

        # Remove T of datetime
        available_times = []
        for date in data:
            list_date = date.split("T")
            new_date = f"{list_date[0]} {list_date[1]}"
            available_times.append(new_date)
        logging.debug("available_times for funnel tour scheduling %s" %available_times)
        data = Data(**{"availableTimes": available_times})
        return data

    def __get_auth_header(self):
        """
        Returns the authentication header dictionary

        Parameters
        ----------
        service_request : Zato Request Object
        """
        encoded_auth = os.environ["FUNNEL_GUEST_CARD_API_KEY"]
        headers = {
        'Accept': 'application/json',
        "Authorization": "Basic %s" % encoded_auth
        }

        return headers

    def __validate(self, params:dict = None, date:str = None,
                   servicerequest:ServiceRequest = None, schema:Enum = None):
        """
        Validates the input payload(firstname, lastname, datecontact)
        and returns the Boolean Value

        Parameters
        ----------
        params: Dictionary
        """
        params = servicerequest.request.payload
        isvalid, _error = DataValidation.schema(schema, params)

        if(_error):
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)

    def book_tour_appointment(self, service_request: ServiceRequest, appointmentData):
        pass

    def __get_from_payload_for_guestcards(self, service_request: ServiceRequest, source_details):
        """
        Framing the Funnel Payload for Tourschedule/Guestcards
        """
        prospect = service_request.request.payload.get(VendorConstants.PROSPECT) and service_request.request.payload[VendorConstants.PROSPECT]
        customer_preference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE)

        desired_bedroom = ''
        desired_rent = ''
        movein_date = ''
        source = ''
        startdate = ''

        if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
            startdate = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]

        if source_details.name:
            source = source_details.name

        if customer_preference:
            if customer_preference.get(VendorConstants.DESIRED_BEDROOM):
                desired_bedroom = get_vendor_layout(VendorLayout.FUNNEL, customer_preference.get(VendorConstants.DESIRED_BEDROOM)
                                                and customer_preference[VendorConstants.DESIRED_BEDROOM])

            desired_rent = customer_preference.get(VendorConstants.DESIRED_RENT) \
                            and customer_preference[VendorConstants.DESIRED_RENT] or None

            movein_date = customer_preference.get(VendorConstants.MOVE_IN_DATE) \
                            and customer_preference[VendorConstants.MOVE_IN_DATE] or None
            movein_date = trim_utc_date(movein_date)
  
        logging.debug('param build completed')
        param_dict = {
                        "client":{
                            "people":[
                                {
                                    "first_name": prospect[VendorConstants.FIRSTNAME],
                                    "last_name": prospect[VendorConstants.LASTNAME],
                                    "email": prospect[VendorConstants.EMAIL],
                                    "phone_1": prospect.get(VendorConstants.PHONE)
                                                and prospect[VendorConstants.PHONE] or ''
                                }
                            ],
                            "move_in_date": movein_date,
                            "layout": desired_bedroom,
                            "price_ceiling": desired_rent,
                            "lead_source": source,
                            "notes": service_request.guest_card_comment
                        }
                    }
        if startdate:
            tour = { "appointment":{
                            "start": startdate,
                            "tour_type": "guided"
                    }}
            param_dict.update(tour)  
        logging.info("payload for funnel %s" %json.dumps(param_dict, indent=4, sort_keys=True))
        return param_dict

    def __get_wsdl(self, service_request):
        """
        returns required WSDL info based on the source
        """
        source = service_request.request.payload.get(VendorConstants.SOURCE) \
                    and service_request.request.payload[VendorConstants.SOURCE].upper() \
                    or service_request.auth.source

        switcher = {FunnelConstants.DH: service_request.auth.DH,
                    FunnelConstants.WS: service_request.auth.WS}

        source_details = ''
        if source in switcher.keys():
            source_details = bunchify(switcher.get(source))

        return source_details
class FunnelGateway:
    """
    Funnel Gateway to connect Funnel service to exchange the data
    """

    def call_funnel(self, conn, cid, body, params, headers, method="POST"):
        """
        Implements All Funnel API Endpoint and returns the response

        Parameters
        ----------
        conn : Outgoing Connection Object
        body : Api request data
        headers : Api Headers
        cid : Zato Connection ID
        params : URL parameters
        method : Http method to call the endpoint

        Returns
        --------
        dict
        """
        try:
            # Connecting Funnel
            if method == "GET":
                response = conn.get(cid, params, headers=headers)
            else:
                if params:
                    response = conn.post(cid, data=body, params=params, headers=headers)
                else:
                    response = conn.post(cid, data=body, headers=headers)
        except Exception as e:
            logging.exception(e.__str__())
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, VendorConstants.BAD_REQUEST)

        # Preparing response object
        response_content = response.json()
        logging.info("response of funnel %s" %response_content)
        return response_content



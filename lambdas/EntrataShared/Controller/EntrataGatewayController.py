import base64
import json
# import logging
import os
import uuid

from cerberus import Validator

from DataPushPullShared.Utilities.Convert import Convert
from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants, DataValidation, Schema
from EntrataShared.Model.EntrataResponse import Leases as eLease
from EntrataShared.Model.EntrataResponse import PropertyCalendarAvailability, TourScheduling
from EntrataShared.Model.EntrataResponse import Resident, Location
from EntrataShared.Utilities.EntrataConstants import EntrataConstants
from EntrataShared.Utilities.EntrataConstants import ResponseSchema
from EntrataShared.Utilities.EntrataMapper import EntrataMapper
from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode, ErrorConstants
from GuestCardShared.Utils.GuestCardResponse import GuestCardResponse, GuestCardInformation, TourInformation
from TourShared.Model.Data_Model import TourAvailabilityData, Data
from TourShared.Utilities.Tour_Constants import Tour_Integration_Constants
from VendorShared.Controller.VendorGatewayController import VendorGatewayController
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.VendorConstants import VendorConstants, VendorLayout, get_vendor_layout
from EntrataShared.Utilities.EntrataUtilities import EntrataResponseGenerator
from VendorShared.Utilities.Utils import trim_utc_date
from Utils import CustomLogger

logging = CustomLogger.logger

class EntrataGatewayController(VendorGatewayController):
    """ 
    EntrataGatewayController class for handling Entrata related communication and data transformations
    """

    def get_residents(self, service_request: ServiceRequest):
        """
        Get residents information from Entrata
        """
        logging.debug("Getting Residents from Entrata")
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]

        # Preparing payload
        _headers = self.__get_auth_header(service_request)

        # Preparing Request Body     
        _body = self.__get_request_body(EntrataConstants.GETCUSTOMERS)
        _body[VendorConstants.METHOD][VendorConstants.PARAMS][EntrataConstants.PROPERTYID] = str(service_request.auth.get_property(EntrataConstants.FORIEGNCOMMUNITYID))

        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.URLCUSTOMERPARAMETER)

        # Host Parameter
        host_params = self.__get_hostparameters()

        # Initiating Entrata service call
        response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                               body=json.dumps(_body), params=_params, headers=_headers, host_params=host_params)
        resident_response = []
        residents = []

        # Validating Response Schema 
        isValid = self.__validate_response_body(ResponseSchema.CUSTOMERS_RESPONSE_FORMAT, response[EntrataConstants.RESPONSE][EntrataConstants.RESULT])
        if (not isValid):
            return residents

        for i in response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.CUSTOMERS][EntrataConstants.CUSTOMER]:
            resident_obj = Resident(**i)
            resident_obj.attributes = i[EntrataConstants.ATTRIBUTES]
            resident_response.append(resident_obj)

        entrata_mapper = EntrataMapper(service_request)
        entrata_response = entrata_mapper.resident_mapper(resident_response)
        return entrata_response

    def get_leases(self, service_request: ServiceRequest):
        """
        Get leasing  information from Entrata
        """
        logging.debug("Getting Leasing from Entrata")
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]

        # Preparing payload
        _headers = self.__get_auth_header(service_request)

        # Preparing Request Body
        _body = self.__get_request_body(EntrataConstants.GETLEASES, {EntrataConstants.INCLEASEHISTORY : True})
        _body[VendorConstants.METHOD][VendorConstants.PARAMS][EntrataConstants.PROPERTYID] = str(service_request.auth.get_property(EntrataConstants.FORIEGNCOMMUNITYID))

        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.URLLEASEPARAMETER)

        # Host Parameter
        host_params = self.__get_hostparameters()

        # Initiating Entrata service call
        response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                               body=json.dumps(_body),  params=_params, headers=_headers, host_params=host_params)
        lease = []

        # Validating Response Schema
        isValid = self.__validate_response_body(ResponseSchema.LEASES_RESPONSE_FORMAT, response[EntrataConstants.RESPONSE][EntrataConstants.RESULT])
        if (not isValid):
            return lease

        leases_obj = eLease(**response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.LEASES])
        entrata_mapper = EntrataMapper(service_request)
        entrata_response = entrata_mapper.leases_mapper(leases_obj)
        return entrata_response

    def get_locations(self, service_request: ServiceRequest):
        """
        Returns the Locations data from Entrata

        Parameters
        ----------
        service_request : Zato Request Object
        """
        logging.debug("Getting Location from Entrata")
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]

        # Preparing payload
        _headers = self.__get_auth_header(service_request)

        # Preparing Request Body  
        _body = self.__get_request_body(EntrataConstants.GETLOCATIONS)
        _body[VendorConstants.METHOD][VendorConstants.PARAMS][EntrataConstants.PROPERTYIDS] = str(service_request.auth.get_property(EntrataConstants.FORIEGNCOMMUNITYID))

        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.URLPROPERTYPARAMETER)

        # Host Parameter
        host_params = self.__get_hostparameters()

        # Initiating Entrata service call
        response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid, body=json.dumps(_body), params= _params, headers=_headers, host_params=host_params)

        location_response = []
        entrata_response = []
        building_list = []

        # Validating Response Schema 
        isValid = self.__validate_response_body(ResponseSchema.LOCATION_RESPONSE_FORMAT, response[EntrataConstants.RESPONSE][EntrataConstants.RESULT])
        if (not isValid):
            return location_response

        for i in response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.PROPERTIES][EntrataConstants.PROPERTY][0][EntrataConstants.UNITS][EntrataConstants.UNIT]:
            location_obj = Location(**i)
            location_response.append(location_obj)
        entrata_mapper = EntrataMapper(service_request)
        entrata_response = entrata_mapper.location_mapper(location_response)
        return entrata_response

    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Returns the Units data from Entrata

        Parameters
        ----------
        service_request : Zato Request Object
        """
        logging.info("Getting Unit Pricing and Availability from Entrata")
        # Payload for unit availability
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]        
        service_payload = service_request.request.payload

        # Preparing payload
        _headers = self.__get_auth_header(service_request)
        
        # Preparing Request Body
        _headers = self.__get_auth_header(service_request)
        _body = self.__get_request_body(EntrataConstants.GETPROPERTIES)
        _body[VendorConstants.METHOD][VendorConstants.PARAMS][EntrataConstants.PROPERTYIDS] = str(service_request.auth.get_property(EntrataConstants.FORIEGNCOMMUNITYID))
        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.PROPERTIES)
        host_params = self.__get_hostparameters()
        propertyresponse = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid, body=json.dumps(_body), params= _params, headers=_headers, host_params=host_params)
        logging.info("Entrata_Property_response: {}".format(propertyresponse))
        # Preparing Request Body
        _headers = self.__get_auth_header(service_request)  
        _body = self.__get_request_body(EntrataConstants.GETUNITANDPRICING)
        _body[VendorConstants.METHOD][VendorConstants.PARAMS][EntrataConstants.PROPERTYID] = str(service_request.auth.get_property(EntrataConstants.FORIEGNCOMMUNITYID))
        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.URLPROPERTYPARAMETER)
        # Host Parameter
        host_params = self.__get_hostparameters()
        # Initiating Entrata service call
        modelresponse = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid, body=json.dumps(_body), params= _params, headers=_headers, host_params=host_params)
        logging.info("Entrata_model_response: {}".format(modelresponse))
        entrata_response_generator = EntrataResponseGenerator()
        unit_available = entrata_response_generator.generate_availability_response(modelresponse, propertyresponse, service_payload)
        logging.info("unit_availablity: {}".format(unit_available))
        return unit_available

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Adds the guestcard data for Entrata

        Parameters
        ----------
        service_request : Zato Request Object
        """
        # Validating Payload Schema
        isvalid, _error = DataValidation.schema(Schema.GUEST_CARDS, service_request.request.payload)

        if(_error):
            raise ValidationError(ErrorCode.ERROR_HTTP_0001, _error)

        # Preparing payload
        _headers = self.__get_auth_header(service_request)

        # Getting parameter from payload
        param_dict = self.__get_from_payload_for_guestcards(service_request, service_request.auth.foreign_community_id, service_request.auth.leadsource_id)

        # Preparing Request Body  
        _body = self.__get_request_body(EntrataConstants.SENDLEADS, param_dict)

        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.LEADS)

        # Host Parameter
        host_params = self.__get_hostparameters()

        #Outgoing Platform Request
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]

        # Initiating Entrata service call
        response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid, body=json.dumps(_body), params= _params, headers=_headers, host_params=host_params)

        # Validating Response Schema 
        isValid = self.__validate_response_body(ResponseSchema.GUESTCARD_RESPONSE_FORMAT, response)
        if (not isValid):
            return response
        else:
            logging.info("success response: {}".format(response))
            output = GuestCardResponse()
            output.guestCardInformation = GuestCardInformation()
            response_1 = response.get(EntrataConstants.RESPONSE).get(EntrataConstants.RESULT).get(EntrataConstants.PROSPECTS).get(EntrataConstants.PROSPECT)[0]
            output.guestCardInformation.guestCardId, output.guestCardInformation.result, output.guestCardInformation.message = response_1.get(EntrataConstants.APPLICATION_ID), response_1.get(EntrataConstants.STATUS), response_1.get(EntrataConstants.MESSAGE)
            response_2 = response_1.get(EntrataConstants.APPLICANTS).get(EntrataConstants.APPLICANT)[0]
            output.guestCardInformation.firstName, output.guestCardInformation.lastName = response_2.get(EntrataConstants.FIRSTNAME), response_2.get(EntrataConstants.LASTNAME)
            output.guestCardInformation.action = VendorConstants.INSERT
            output.guestCardInformation.status = VendorConstants.NEW
            if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
                output.tourInformation = TourInformation()
                output.tourInformation.tourSchedule = True
                output.tourInformation.tourRequested = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
            else:
                output.__delattr__(VendorConstants.TOUR_INFORMATION)
        return output

    def get_tour_availabilities(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):
        """
        Get tour availabilities information from Entrata
        """
        logging.info("Getting tour availabilities from Entrata")
        outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]

        # Preparing payload
        _headers = self.__get_auth_header(service_request)

        # Preparing Request Body
        params = {EntrataConstants.PROPERTYID: service_request.auth.foreign_community_id,
                  EntrataConstants.FROM_DATE: Convert.format_date(tour_availability_data.fromDate,
                                                                  EntrataConstants.QUEXT_DATE_FORMAT,
                                                                  EntrataConstants.ENTRATA_DATE_FORMAT),
                  EntrataConstants.TO_DATE: Convert.format_date(tour_availability_data.toDate,
                                                                EntrataConstants.QUEXT_DATE_FORMAT,
                                                                EntrataConstants.ENTRATA_DATE_FORMAT)}
        _body = self.__get_request_body(method=EntrataConstants.GET_CALENDAR_AVAILABILITY, params_optional=params)

        # Parameters get replaced into the url template
        _params = self.__get_parameters(EntrataConstants.PROPERTIES)

        # Host Parameter
        host_params = self.__get_hostparameters()

        # Initiating Entrata service call
        response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid,
                                                 body= json.dumps(_body), params= _params, 
                                                 headers=_headers, host_params=host_params)
        # Checking for Empty list
        if response[EntrataConstants.RESPONSE].get(EntrataConstants.RESULT).get(EntrataConstants.SUCCESS):
            logging.info("Got no records for Tour Availability from Entrata")
            return []
        res = (response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][
                EntrataConstants.PROPERTY_CALENDAR_AVAILABILITY])
        for value in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            start_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.START_TIME]
            end_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.END_TIME]
            
            start_time = Convert.convert_datetime_timezone(start_time, EntrataConstants.ENTRATA_TIMEZONE,
                                                             EntrataConstants.QUEXT_TIMEZONE,  
                                                             EntrataConstants.DATETIME_FORMAT, 
                                                             Tour_Integration_Constants.DATETIME)
            end_time = Convert.convert_datetime_timezone(end_time, EntrataConstants.ENTRATA_TIMEZONE, 
                                                            EntrataConstants.QUEXT_TIMEZONE, 
                                                            EntrataConstants.DATETIME_FORMAT, 
                                                            Tour_Integration_Constants.DATETIME)
            start_time = start_time.split(' ')
            end_time = end_time.split(' ')
            if start_time[0] and end_time[0]:
                value[EntrataConstants.DATE] = start_time[0]
                value[EntrataConstants.START_TIME] = start_time[1]
                value[EntrataConstants.END_TIME] = end_time[1]
        time_slot = []
        for items in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            starttime = items[EntrataConstants.DATE] + 'T'+ items[EntrataConstants.START_TIME]
            endtime = items[EntrataConstants.DATE] + 'T' + items[EntrataConstants.END_TIME]
            time_slot.append({EntrataConstants.START_TIME: starttime, EntrataConstants.END_TIME: endtime })
            availableTimes = Convert.generate_time_slots(time_slot)
        data = Data(**{"availableTimes": availableTimes})
        return data
    
    # Currently Tour Scheduling is handled with Guestcard creation. Hence commenting below method.
    # def book_tour_appointment(self, service_request: ServiceRequest, appointmentData):

    #     outgoing_platform_request = service_request.outgoing.plain_http[EntrataConstants.ENTRATA_CHANNEL_NAME]
    #     # Preparing payload
    #     _headers = self.__get_auth_header(service_request)

    #     # Getting parameter from payload
    #     param_dict = self.__payload_for_booktour(service_request, appointmentData)

    #     # Preparing Request Body  
    #     _body = self.__get_request_body(EntrataConstants.SENDLEADS, param_dict)
    #     # Parameters get replaced into the url template
    #     _params = self.__get_parameters(EntrataConstants.LEADS)

    #     # Host Parameter
    #     host_params = self.__get_hostparameters(service_request.auth.UserName)

    #     # Initiating Entrata service call
    #     response = EntrataGateway().call_entrata(conn=outgoing_platform_request.conn, cid=service_request.cid, body=json.dumps(_body), params= _params, headers=_headers, host_params=host_params)

    #     # Validating Response Schema 
    #     isValid = self.__validate_response_body(ResponseSchema.BOOK_TOUR_RESPONSE_FORMAT, response[EntrataConstants.RESPONSE][EntrataConstants.RESULT])
    #     if (not isValid):
    #         return response

    #     booktour_obj = TourScheduling(**response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][
    #                         EntrataConstants.PROSPECTS][EntrataConstants.PROSPECT][0])
    #     booktour_obj.id = response[EntrataConstants.RESPONSE][EntrataConstants.REQUEST_ID]

    #     return booktour_obj

    def __get_auth_header(self, service_request: ServiceRequest):
        """
        Returns the authentication header dictionary

        Parameters
        ----------
        service_request : Zato Request Object
        """
        auth_header = "{}:{}".format(service_request.auth.UserName,service_request.auth.Password)
        encoded_auth = base64.b64encode(auth_header.encode("utf-8")).decode("utf-8")
        headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic %s" % encoded_auth
        }

        return headers

    def __get_request_body(self,method: str = "", params_optional:dict = None):
        """
        Returns the request dictionary 

        Parameters
        ----------
        method : API Method (GetCustomer , GetLeases , etc)
        params_optional: Dict (extra params)
        """
        request_body ={
                  "auth": {
                    "type": "basic"
                  },
                  "requestId": str(uuid.uuid1()),
                  "method": {
                    "name": str(method),
                    "version": "r1",
                    "params": {
                    }
                  }
            }

        if(params_optional):
            request_body[VendorConstants.METHOD][VendorConstants.PARAMS].update(params_optional)

        return request_body

    def __get_parameters(self, method: str = ""):
        """
        Returns the URL parameters 

        Parameters
        ----------
        method : URL Method (properties , customers , etc)
        """
        params = {
                   "method": str(method)
            }

        return params

    def __get_hostparameters(self):
        """
        Returns the host parameters 

        Parameters
        ----------
        subdomain : Host subdomain (primeplacellc , etc)
        """
        params = {
                   "subdomain": str(os.getenv("ENTRATA_SUBDOMAIN"))
            }

        return params

    def __validate_response_body(self, schema:str = "", body:dict = None):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        v = Validator()
        isValid = v.validate(body, schema)

        return isValid

    def __get_from_payload_for_guestcards(self, service_request: ServiceRequest, property_id, lead_source_id):

        prospect = service_request.request.payload.get(VendorConstants.PROSPECT) and service_request.request.payload[VendorConstants.PROSPECT]
        
        customer_preference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE)
        
        contact_types = ''
        desired_bedroom = ''
        desired_bathroom = ''
        desired_rent = ''
        occupants = ''
        lease_term_months = ''
        preferred_amenities = ''
        movein_date = ''
        if customer_preference:
            contact_types = [ customer_preference.get(VendorConstants.CONTACT_PREFERENCE) and item.lower()
                            for item in customer_preference.get(VendorConstants.CONTACT_PREFERENCE) or None]

            desired_bedroom = get_vendor_layout(VendorLayout.ENTRATA, customer_preference.get(VendorConstants.DESIRED_BEDROOM)
                                                and customer_preference[VendorConstants.DESIRED_BEDROOM])

            desired_bathroom = customer_preference.get(VendorConstants.DESIRED_BATHROOM) \
                                and customer_preference[VendorConstants.DESIRED_BATHROOM] or []
            
            desired_rent = customer_preference.get(VendorConstants.DESIRED_RENT) \
                            and customer_preference[VendorConstants.DESIRED_RENT] or None

            occupants = customer_preference.get(VendorConstants.NO_OF_OCCUPANTS) \
                        and customer_preference[VendorConstants.NO_OF_OCCUPANTS] or None

            lease_term_months = customer_preference.get(VendorConstants.LEASE_TERM_MONTHS) \
                            and customer_preference[VendorConstants.LEASE_TERM_MONTHS] or None

            preferred_amenities = customer_preference.get(VendorConstants.PREFERRED_AMENITIES) \
                                    and customer_preference[VendorConstants.PREFERRED_AMENITIES] or None
            
            move_in_date = customer_preference.get(VendorConstants.MOVE_IN_DATE) \
                            and customer_preference[VendorConstants.MOVE_IN_DATE] or None
            move_in_date = trim_utc_date(move_in_date)

            movein_date = move_in_date and Convert.format_date(move_in_date, 
                                                                EntrataConstants.QUEXT_DATE_FORMAT,
                                                                 EntrataConstants.ENTRATA_DATE_FORMAT)
        
        logging.debug('param build completed')
        param_dict = {
            "propertyId": property_id,
            "prospects": {
                "prospect": {
                    "leadSource": {
                        "originatingLeadSourceId": lead_source_id
                    },
                    "createdDate": Convert.get_msttz(),
                    "customers": {
                        "customer": {
                            "name": {
                                "firstName": prospect[VendorConstants.FIRSTNAME],
                                "lastName": prospect[VendorConstants.LASTNAME]
                            },
                            "phone": {
                                "personalPhoneNumber": prospect.get(VendorConstants.PHONE)
                                                       and prospect[VendorConstants.PHONE] or ''
                            },
                            "email": prospect[VendorConstants.EMAIL] or '',
                            "marketingPreferences": {
                                "email": {
                                    "optInLeadCommunication": EntrataConstants.EMAIL in contact_types and "1" or "0",
                                    "optInMessageCenter": "0",
                                    "optInContactPoints": EntrataConstants.EMAIL in contact_types and "1" or "0",
                                    "optInMarketingMessages": "0"
                                },
                                "optInphone": EntrataConstants.PHONE in contact_types and "1" or "0",
                                "optInMail": "0"
                            }
                        }
                    },
                    "customerPreferences": {
                        "desiredMoveInDate": movein_date,
                        "desiredRent": {
                            "min": desired_rent,
                            "max": desired_rent
                        },
                        "desiredNumBedrooms": desired_bedroom,
                        "desiredNumBathrooms": desired_bathroom,
                        "desiredLeaseTerms": lease_term_months,
                        "numberOfOccupants": occupants,
                        "comment": service_request.guest_card_comment + preferred_amenities
                    },
                    "events": {
                        "event": [
                            {
                                "typeId": EntrataConstants.GUESTCARD_ID,
                                "type": EntrataConstants.GUESTCARD_METHOD,
                                "date": Convert.get_msttz(),
                                "eventReason": move_in_date
                            }
                        ]
                    }
                }
            }
        }

        if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
            startdate = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
            startdate = Convert.convert_datetime_timezone(startdate, EntrataConstants.QUEXT_TIMEZONE,
                                                          EntrataConstants.ENTRATA_TIMEZONE,
                                                          Tour_Integration_Constants.TOURSTART_FORMAT,
                                                          EntrataConstants.DATETIME_FORMAT)
            startdate = startdate.replace(' ', 'T')
            events = {
                "type": EntrataConstants.BOOK_TOUR_EVENT,
                "date": Convert.get_msttz(),
                "comments": service_request.request.payload[VendorConstants.CUSTOMER_PREFERENCE]
                [VendorConstants.MOVE_IN_REASON],
                "eventReasonId": service_request.auth.eventreason_id
            }

            param_dict[EntrataConstants.PROSPECTS][EntrataConstants.PROSPECT] \
                [EntrataConstants.EVENTS][EntrataConstants.EVENT].append(events)
        return param_dict

    # Currently Tour Scheduling is handled with Guestcard creation. Hence commenting below method.
    # def __payload_for_booktour(self, service_request: ServiceRequest, appointmentData):

    #     logging.info('preparing payload for book tour')
    #     start_date = Convert.convert_datetime_timezone(appointmentData.start,'GMT','MST',Tour_Integration_Constants.DATETIME, EntrataConstants.DATETIME_FORMAT)
    #     start_date = start_date.replace(' ','T')
    #     param_dict = {
    #         "propertyId": service_request.auth.foreign_community_id,
    #         "prospects": {
    #             "prospect": {
    #                 "leadSource": {
    #                     "originatingLeadSourceId": service_request.auth.leadsource_id
    #                 },
    #                 "createdDate": Convert.get_msttz(),
    #                 "customers": {
    #                     "customer": {
    #                         "name": {
    #                             "firstName": appointmentData.firstName,
    #                             "lastName": appointmentData.lastName
    #                         },
    #                         "phone": {
    #                             "personalPhoneNumber": appointmentData.phone
    #                         },
    #                         "email": appointmentData.email
    #                     }
    #                 },
    #                 "customerPreferences": {
    #                     "desiredMoveInDate": appointmentData.moveInDate,
    #                     "desiredRent": {
    #                         "min": appointmentData.priceCeiling,
    #                         "max": appointmentData.priceCeiling
    #                     },
    #                     "desiredNumBedrooms": appointmentData.layout[0],
    #                     "comment": appointmentData.notes
    #                 },
    #                 "events": {
    #                     "event": [
    #                         {
    #                             "type": EntrataConstants.BOOK_TOUR_EVENT,
    #                             "date": start_date,
    #                             "comments": appointmentData.notes,
    #                             "eventReasonId": service_request.auth.eventreason_id
    #                         }
    #                     ]
    #                 }
    #             }
    #         }
    #     }
    #     return param_dict


class EntrataGateway:
    """
    Entratagateway to connect Entrata service to exchange the data
    """

    def call_entrata(self, conn, cid, body, params, headers, host_params):
        """
        Implements All ResMan API Endpoint and returns the response

        Parameters
        ----------
        conn : Outgoing Connection Object
        body : Api request data
        headers : Api Headers
        cid : Zato Connection ID
        params : URL parameters

        Returns
        --------
        dict
        """
        try:
            # Connecting Entrata
            conn.config['address_host']=conn.config['address_host'].format(**host_params)
            conn.address = '{}{}'.format(conn.config['address_host'], conn.config['address_url_path'])
            logging.info("Request Body:{}".format(body))
            response = conn.post(cid, data=body, params=params, headers=headers)
        except Exception as e:
            logging.exception(e.__str__())
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, VendorConstants.BAD_REQUEST)

        # Preparing response object             
        response_content = response.json()
        # Checking the status of the response        
        if response.status_code != 200:
            logging.error("Invalid Response : {}".format(response_content))
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_DATA, response.status_code)

        if response.status_code == 200 and (response_content[EntrataConstants.RESPONSE].get(QuextIntegrationConstants.ERROR) or response_content[EntrataConstants.RESPONSE].get(QuextIntegrationConstants.CODE) == 300):
            logging.error("Invalid Response : {}".format(response_content))
            raise GatewayError(ErrorCode.ERROR_HTTP_0001, ErrorConstants.INVALID_REQUEST + " or configuration -> " + json.dumps(response_content[EntrataConstants.RESPONSE].get(QuextIntegrationConstants.RESULT)), QuextIntegrationConstants.HTTP_BAD_RESPONSE_CODE)

        return response_content

from datetime import datetime, date, timedelta

from zeep import Client
from lxml import etree
import xmltodict
from bunch import bunchify
from enum import Enum
import dateutil.parser
import json

from cerberus import Validator

from VendorShared.Controller.VendorGatewayController import VendorGatewayController
from VendorShared.Model.ServiceRequest import ServiceRequest
from RealpageShared.Utilities.RealpageConstants import RealpageConstants
from DataPushPullShared.Utilities.DataController import DataValidation, Schema, Validation_Schema
from ExceptionHandling.Model.Exceptions import ValidationError
from ExceptionHandling.Utilities.ErrorCode import ErrorCode
from RealpageShared.Utilities.RealPageUnitResponse import RealPageUnitResponse
from GuestCardShared.Utils.GuestCardResponse import  GuestCardResponse, GuestCardInformation, TourInformation
from TourShared.Model.Data_Model import TourAvailabilityData, Data
from VendorShared.Utilities.VendorConstants import VendorConstants, VendorLayout, get_vendor_layout
from DataPushPullShared.Utilities.Convert import Convert
from VendorShared.Utilities.Utils import trim_utc_date
from Utils import CustomLogger

logging = CustomLogger.logger


class RealpageGatewayController(VendorGatewayController):
    """ 
    RealpageGatewayController class for handling Entrata related communication and data transformations
    """

    def get_residents(self, service_request: ServiceRequest):
        """
        Get residents information from Realpage
        """
        pass     

    def get_leases(self, service_request: ServiceRequest):
        """
        Get leasing  information from Realpage
        """
        pass

    def get_locations(self, service_request: ServiceRequest):
        """
        Returns the Locations data from Realpage

        Parameters
        ----------
        service_request : Zato Request Object
        """
        pass

    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Get unit information
        """
        logging.debug("Unit Availability: RealPage")
        wsdl_source = service_request.auth.source
        auth = wsdl_source and bunchify(service_request.auth.get_property(wsdl_source)) or bunchify(service_request.auth.DH)
        client = service_request.outgoing.soap.client(auth.wsdl)
        factory = client.type_factory(RealpageConstants.FACTORY_DATA_STRUCTURE)
        # Preparing auth details from service request
        _auth = factory.AuthDTO(pmcid=auth.pmcid,
                                siteid=auth.siteid,
                                licensekey=auth.licensekey)

        res = client.service.getunitlist(auth=_auth)
        response = xmltodict.parse(etree.tostring(res))
        format_response = RealPageUnitResponse()
        output = format_response.unit_availability_response(response["GetUnitList"]["UnitObjects"]["UnitObject"])
        return output

    def get_tour_availabilities(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):
        """
        Get tour available information
        """
        """
        Get tour availability from Realpage
        """
        logging.debug("Availability: RealPage")

        source_details = self.__get_wsdl(service_request)
         # creating client connection
        client = Client(wsdl=source_details.wsdl)

        date_diff = datetime.strptime(tour_availability_data.toDate, RealpageConstants.DAYFORMAT) - \
                    datetime.strptime(tour_availability_data.fromDate, RealpageConstants.DAYFORMAT)
        toDate = tour_availability_data.toDate
        if date_diff.days > 7:
            toDate = (datetime.strptime(tour_availability_data.fromDate, RealpageConstants.DAYFORMAT) + \
                        timedelta(days=7)).strftime(RealpageConstants.DAYFORMAT)
        if client: 
            factory = client.type_factory(RealpageConstants.FACTORY_DATA_STRUCTURE)
            
            # Preparing auth details from service request
            _auth = factory.AuthDTO(pmcid=source_details.pmcid, 
                                    siteid=source_details.siteid, 
                                    licensekey=source_details.licensekey)
            
            getappointmenttimesparam = factory.getappointmenttimesparam(
                                    checkall=RealpageConstants.CHECK_ALL, 
                                    leasingagentid=RealpageConstants.LEASING_AGENT_ID, 
                                    startdatetime=tour_availability_data.fromDate + RealpageConstants.START_TIME,
                                    enddatetime=toDate + RealpageConstants.END_TIME)

            response = client.service.getagentsappointmenttimes(
                                    auth=_auth, 
                                    getappointmenttimesparam=getappointmenttimesparam)

            result = xmltodict.parse(etree.tostring(response))
            v = Validator()
            v.allow_unknown = True
            result = xmltodict.parse(etree.tostring(response))
            isValid = v.validate(result, Validation_Schema[Schema.REAL_PAGE_GET_AGENT_APPOINTMENT_TIME])                               
            
            response_list = []
            logging.debug("Generate Available Dates output")
            if isValid:  
               for i in result["getagentsappointmenttimes"]['leasingagent']:
                    if i.get('availabledates') and isinstance(i['availabledates']['availabledate'],list):
                        response_list.extend(i['availabledates']['availabledate'])
                    elif i.get('availabledates') and isinstance(i['availabledates']['availabledate'],dict):
                        response_list.append(i['availabledates']['availabledate'])   
                    availableTimes = Convert.generate_time_slots(response_list)

                    data = Data(**{"availableTimes": availableTimes})
            return data 

    def book_tour_appointment(self, service_request: ServiceRequest, appointmentData):
        """
        Post book tour appointment
        """
        pass

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Adds the guestcard data for Realpage

        Parameters
        ----------
        service_request : Zato Request Object
        """
        logging.debug("Guest Cards: RealPage")
        self.__validate(servicerequest=service_request, schema=Schema.GUEST_CARDS)  # Method to validate request payload        

        source_details = self.__get_wsdl(service_request)
        # creating client connection
        client = Client(wsdl=source_details.wsdl)
        if client:
            factory = client.type_factory(RealpageConstants.FACTORY_DATA_STRUCTURE)

            # Preparing auth details from service request
            _auth = factory.AuthDTO(pmcid=source_details.pmcid, 
                                    siteid=source_details.siteid, 
                                    licensekey=source_details.licensekey)
            prospect = service_request.request.payload.get(VendorConstants.PROSPECT) \
                        and service_request.request.payload[VendorConstants.PROSPECT] or None
            
            # Fetching Phone number details
            _phone_number = factory.PhoneNumber(type=RealpageConstants.HOME,
                                                number=prospect.get(VendorConstants.PHONE) \
                                                and prospect[VendorConstants.PHONE] or None)
            array_of_phone_number = factory.ArrayOfPhoneNumber(_phone_number)
            # Getting prospect details from payload
            _prospect = factory.Prospect(
                            firstname=prospect[VendorConstants.FIRSTNAME]
                            ,lastname=prospect[VendorConstants.LASTNAME]
                            ,email=prospect[VendorConstants.EMAIL] and prospect[VendorConstants.EMAIL] \
                                        or None
                            ,relationshipid= RealpageConstants.RELATIONSHIP_ID
                            ,numbers=factory.Numbers(phonenumbers=array_of_phone_number))
            
            logging.info("prospect data")
            logging.info(_prospect)
            # comment = service_request.request.payload.get(VendorConstants.COMMENT) \
            #             and service_request.request.payload[VendorConstants.COMMENT] or None
            comment = service_request.guest_card_comment
            datecontact = datetime.now().strftime(RealpageConstants.TIMEFORMAT)

            
            # date followup is fixed as 3 days from date contact
            datefollowup = datetime.strptime(datecontact, RealpageConstants.TIMEFORMAT) + \
                        timedelta(days=source_details.datefollowup)

            customerpreference = service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE)

            move_in_date = customerpreference.get(VendorConstants.MOVE_IN_DATE) \
                                and customerpreference[VendorConstants.MOVE_IN_DATE] or datetime.now().strftime("%Y-%m-%dT00:00:00Z")
            move_in_date = trim_utc_date(move_in_date)

            _preferences = ''
            _preferences = factory.Preferences (dateneeded=move_in_date)
            leadsource_id = ''
            contactpreferences = ''
            moveinreason = ''
            preferred_amenities = ''
            floorplangroupid = ''
            
            logging.info("preference Data")            
            logging.info(_preferences)
            
            if service_request.request.payload.get(VendorConstants.CUSTOMER_PREFERENCE):

                if service_request.auth.source == RealpageConstants.DH:
                    leadsourceid = xmltodict.parse(etree.tostring(client.service.getmarketingsourcesbyproperty(auth=_auth)))
                    _leadsourceid = [item[RealpageConstants.VALUE] \
                                    for item in leadsourceid[RealpageConstants.MARKETING_PROPERTY] \
                                        [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM] \
                                        if RealpageConstants.QUEXT in item[RealpageConstants.TEXT].lower()]


                    leadsource_id = _leadsourceid[0] if len(_leadsourceid) > 0 else ""

                    desired_bedroom = get_vendor_layout(VendorLayout.REALPAGE,
                                                        customerpreference.get(VendorConstants.DESIRED_BEDROOM)
                                                        and customerpreference[VendorConstants.DESIRED_BEDROOM] or [] )

                    desired_bathroom = customerpreference.get(VendorConstants.DESIRED_BATHROOM) \
                                        and customerpreference[VendorConstants.DESIRED_BATHROOM] or []

                    _floorplangroupid = xmltodict.parse(etree.tostring(client.service.getfloorplangroupsbyproperty(auth=_auth)))


                    floorplangroupid = []
                    for values in _floorplangroupid[RealpageConstants.GET_FLOORPLANGROUP_ID] \
                                                    [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                        if values[RealpageConstants.TEXT][0] in desired_bedroom:
                            floorplangroupid.append(values[RealpageConstants.VALUE])
                            if values[RealpageConstants.TEXT][2] in desired_bathroom:
                                floorplangroupid.append(values[RealpageConstants.VALUE])

                    floorplangroupid = ",".join(floorplangroupid)
                    # if payload contains pricing parameter to add in preferences
                    price_ceiling = customerpreference[VendorConstants.DESIRED_RENT] \
                                    if customerpreference.get(VendorConstants.DESIRED_RENT) else None
                    pricerangeid = ""
                    if price_ceiling:
                        # Convert input value to float
                        input_val = float(price_ceiling)
                        # getpricerangesbyproperty
                        price_range = xmltodict.parse(etree.tostring(client.service.getpricerangesbyproperty(auth=_auth)))
                        # price_range = xmltodict.parse(etree.tostring(_price_range))
                        for values in price_range[RealpageConstants.GET_PRICE_RANGE][RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                            # Split range value into start and end values
                            start, end = values[RealpageConstants.TEXT].split("-")
                            # Convert start and end values to floats
                            start_value = float(start.strip())
                            end_value = float(end.strip())
                            # Check if input value is within range
                            if start_value <= input_val <= end_value:
                                pricerangeid = (values[RealpageConstants.VALUE])

                    contacttypes = customerpreference.get(VendorConstants.CONTACT_PREFERENCE) \
                                    and [item.lower() for item in customerpreference
                                    [VendorConstants.CONTACT_PREFERENCE]] or None
                    _contacttypes =  xmltodict.parse(etree.tostring(client.service.getallcontacttypes(auth=_auth)))

                    contact_preference = []
                    for values in _contacttypes[RealpageConstants.GET_ALL_CONTACT_TYPE] \
                                                [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                        if values[RealpageConstants.TEXT].lower() in contacttypes:
                            contact_preference.append(values[RealpageConstants.VALUE])

                    contactpreferences = contact_preference[0]

                    movein_reason = customerpreference.get(VendorConstants.MOVE_IN_REASON) \
                                    and customerpreference[VendorConstants.MOVE_IN_REASON] or None

                    _moveinreason =  xmltodict.parse(etree.tostring(client.service.getreasonsformoving(auth=_auth)))
                    moveinreason = ""
                    for values in _moveinreason[RealpageConstants.GET_REASON_FOR_MOVING] \
                                                [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                        if values[RealpageConstants.TEXT].lower() in movein_reason.lower():
                            moveinreason = values[RealpageConstants.VALUE]

                    occupants = customerpreference.get(VendorConstants.NO_OF_OCCUPANTS) \
                                and customerpreference[VendorConstants.NO_OF_OCCUPANTS] or None

                    leasetermmonths = customerpreference.get(VendorConstants.LEASE_TERM_MONTHS) \
                                        and customerpreference[VendorConstants.LEASE_TERM_MONTHS] or None

                    preferred_amenities = customerpreference.get(VendorConstants.PREFERRED_AMENITIES) \
                                            and customerpreference[VendorConstants.PREFERRED_AMENITIES] or None

                    # move_in_date = customerpreference.get(VendorConstants.MOVE_IN_DATE) \
                    #             and customerpreference[VendorConstants.MOVE_IN_DATE] or datetime.now().strftime("%Y-%m-%d")

                #floorplangroupid = ",".join(floorplangroupid)
                # if payload contains pricing parameter to add in preferences
                price_ceiling = customerpreference[VendorConstants.DESIRED_RENT] \
                                if customerpreference.get(VendorConstants.DESIRED_RENT) else None
                pricerangeid = ""
                if price_ceiling:
                    # Convert input value to float
                    input_val = float(price_ceiling)
                    # getpricerangesbyproperty
                    price_range = xmltodict.parse(etree.tostring(client.service.getpricerangesbyproperty(auth=_auth)))
                    # price_range = xmltodict.parse(etree.tostring(_price_range))
                    for values in price_range[RealpageConstants.GET_PRICE_RANGE][RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                        # Split range value into start and end values
                        start, end = values[RealpageConstants.TEXT].split("-")
                        # Convert start and end values to floats
                        start_value = float(start.strip())
                        end_value = float(end.strip())
                        # Check if input value is within range
                        if start_value <= input_val <= end_value:
                            pricerangeid = (values[RealpageConstants.VALUE])

                contacttypes = customerpreference.get(VendorConstants.CONTACT_PREFERENCE) \
                                and [item.lower() for item in customerpreference 
                                [VendorConstants.CONTACT_PREFERENCE]] or None
                _contacttypes =  xmltodict.parse(etree.tostring(client.service.getallcontacttypes(auth=_auth)))
                
                contact_preference = []
                for values in _contacttypes[RealpageConstants.GET_ALL_CONTACT_TYPE] \
                                            [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                    if values[RealpageConstants.TEXT].lower() in contacttypes:
                        contact_preference.append(values[RealpageConstants.VALUE])

                contactpreferences = contact_preference[0]

                movein_reason = customerpreference.get(VendorConstants.MOVE_IN_REASON) \
                                and customerpreference[VendorConstants.MOVE_IN_REASON] or None

                _moveinreason =  xmltodict.parse(etree.tostring(client.service.getreasonsformoving(auth=_auth)))
                moveinreason = ""
                for values in _moveinreason[RealpageConstants.GET_REASON_FOR_MOVING] \
                                            [RealpageConstants.CONTENTS][RealpageConstants.PICKLIST_ITEM]:
                    if values[RealpageConstants.TEXT].lower() in movein_reason.lower():
                        moveinreason = values[RealpageConstants.VALUE]

                occupants = customerpreference.get(VendorConstants.NO_OF_OCCUPANTS) \
                            and customerpreference[VendorConstants.NO_OF_OCCUPANTS] or None

                leasetermmonths = customerpreference.get(VendorConstants.LEASE_TERM_MONTHS) \
                                    and customerpreference[VendorConstants.LEASE_TERM_MONTHS] or None

                preferred_amenities = customerpreference.get(VendorConstants.PREFERRED_AMENITIES) \
                                        and customerpreference[VendorConstants.PREFERRED_AMENITIES] or None

                move_in_date = customerpreference.get(VendorConstants.MOVE_IN_DATE) \
                            and customerpreference[VendorConstants.MOVE_IN_DATE] or datetime.now().strftime("%Y-%m-%dT00:00:00Z")
                move_in_date = trim_utc_date(move_in_date)

                _preferences = factory.Preferences (dateneeded=move_in_date
                                                    ,pricerangeid=pricerangeid
                                                    ,floorplangroupid=floorplangroupid
                                                    ,leasetermmonths=leasetermmonths
                                                    ,occupants=occupants)

            #genereate tour scheduling data if tour_included and tour_data is valid
            appointment = ""
            if service_request.request.payload.get(VendorConstants.TOUR_SCHEDULE_DATA):
                date_str = dateutil.parser.parse(service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START])             

                appointment = factory.Appointment(day=date_str.day, hour=date_str.hour,
                                        minute=date_str.minute, month=date_str.month,
                                        year=date_str.year, leasingagentid=RealpageConstants.LEASING_AGENT_ID)
   
                _guestcard = factory.GuestCard(
                            datecontact = datecontact, 
                            datefollowup = datefollowup,
                            prospects = factory.ArrayOfProspect(_prospect), 
                            createdate = date.today(),
                            statusisactive = RealpageConstants.STATUS_IS_ACTIVE, 
                            statusisleased = RealpageConstants.STATUS_IS_LEASED, 
                            statusislost = RealpageConstants.STATUS_IS_LOST,
                            skipduplicatecheck = RealpageConstants.SKIP_DUPLICATE_CHECK, 
                            daysbackduplicatecheck = RealpageConstants.DAYS_BACK_DUPLICATE_CHECK,
                            appointment = appointment,
                            preferences = _preferences,
                            contacttype = contactpreferences,
                            moveinreason = moveinreason,
                            optionaltasknotes = preferred_amenities,
                            prospectcomment = comment,
                            primaryleadsource = leadsource_id
                            )
                tour_response = {
                                    "tourSchedule": True,
                                }
            else:
            # Generating guestcard details
                _guestcard = factory.GuestCard(
                                datecontact = datecontact, 
                                datefollowup = datefollowup,
                                prospects = factory.ArrayOfProspect(_prospect), 
                                createdate = date.today(),
                                statusisactive = RealpageConstants.STATUS_IS_ACTIVE, 
                                statusisleased = RealpageConstants.STATUS_IS_LEASED, 
                                statusislost = RealpageConstants.STATUS_IS_LOST,
                                skipduplicatecheck = RealpageConstants.SKIP_DUPLICATE_CHECK, 
                                daysbackduplicatecheck = RealpageConstants.DAYS_BACK_DUPLICATE_CHECK,
                                preferences = _preferences,
                                contacttype = contactpreferences,
                                moveinreason = moveinreason,
                                optionaltasknotes = preferred_amenities,
                                prospectcomment = comment,
                                primaryleadsource = leadsource_id
                                )
            logging.info("from RealPage")
            logging.info(_guestcard)
            response = xmltodict.parse(etree.tostring(client.service.insertprospect(auth=_auth, \
                                        guestcard=_guestcard)))
            response_dict = response.get(RealpageConstants.INSERT_PROSPECT_RESPONSE) \
                            and response.get(RealpageConstants.INSERT_PROSPECT_RESPONSE)[RealpageConstants.GUESTCARD]           
            res = GuestCardResponse()
            if response_dict:
                res.guestCardInformation = GuestCardInformation(**response_dict)
                res.guestCardInformation.firstName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.FIRSTNAME]
                res.guestCardInformation.lastName = service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.LASTNAME]
                res.guestCardInformation.guestCardId = response_dict[RealpageConstants.ID]
                if appointment:
                    res.tourInformation = TourInformation(**tour_response)
                    if VendorConstants.TOUR_SCHEDULE_DATA in service_request.request.payload:
                        res.tourInformation.tourRequested = service_request.request.payload[VendorConstants.TOUR_SCHEDULE_DATA][VendorConstants.START]
                        res.tourInformation.tourScheduledID = response_dict[RealpageConstants.ID]
                return res
            res.guestCardInformation = GuestCardInformation(FirstName=service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.FIRSTNAME] \
                                    ,LastName=service_request.request.payload[VendorConstants.PROSPECT][VendorConstants.LASTNAME])
            return res

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
    
    def __get_wsdl(self, service_request):
        """
        returns required WSDL info based on the source
        """
        source = service_request.request.payload.get(VendorConstants.SOURCE) \
                    and service_request.request.payload[VendorConstants.SOURCE].upper() \
                    or service_request.auth.source
        
        switcher = {RealpageConstants.DH: service_request.auth.DH,
                    RealpageConstants.WS: service_request.auth.WS}
        
        source_details = ''
        if source in switcher.keys():
            source_details = bunchify(switcher.get(source))
        return source_details
    
    

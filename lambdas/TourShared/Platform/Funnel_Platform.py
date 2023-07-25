import json
import logging

from TourShared.Interface.Platform_Interface import PlatformInterface
from TourShared.Model.Data_Model import Layout_Type, BasePlatformData, TourAvailabilityData, AppointmentData
from TourShared.Utilities.Data_Validation import DataValidation
from TourShared.Utilities.Tour_Constants import Tour_Integration_Constants
import base64
import dateutil.parser


class FunnelPlatformData(BasePlatformData):
    def __init__(self, _communityID: str, _apiToken: str) -> None:
        self.communityID = _communityID
        self.apiToken = _apiToken


class Appointment:
    def __init__(self, start):
        self.start = start


class Person:
    def __init__(self, first_name, last_name, email, phone_1):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_1 = phone_1


class Client:
    def __init__(self, people, move_in_date, layout, price_ceiling, lead_source, notes):
        self.people = people
        self.move_in_date = move_in_date
        self.layout = layout
        self.price_ceiling = price_ceiling
        self.lead_source = lead_source
        self.discovery_source = lead_source
        self.notes = notes


class FunnelTourScheduleBodyClass:
    def __init__(self, appointment, client):
        self.appointment = appointment
        self.client = client


class FunnelTourAvailabilityClass:
    def __init__(self, group_id: str, from_date: str, to_date: str):
        self.group_id = group_id
        self.from_date = from_date
        self.to_date = to_date


class Funnel_Constants:
    GROUP_ID = 'group_id'
    AUTHORIZATION = 'Authorization'
    ASCII = 'ascii'
    API_TOKEN = 'apiToken'
    COMMUNITY_ID = 'communityID'


def get_platform_lead_source(_type):
    switcher = {
        'DIGITAL HUMAN': "Digital Human",
        'WEBSITE': 'Website'
    }
    return switcher.get(_type, 20)


def get_funnel_room_layout(_layout):
    """
         @desc: this method will check for the _layout list and returns the converted list.
         @param: _layout list which contains the list of layouts the prospect wish to take tour.
         @return: a converted(platform dependent) list of layouts.
    """
    data = []
    switcher = {
        Layout_Type.ONE_BEDROOM: '1br',
        Layout_Type.TWO_BEDROOM: '2br',
        Layout_Type.THREE_BEDROOM: '3br',
        Layout_Type.FOUR_BEDROOM: '4+br',
        Layout_Type.STUDIO: 'studio',
        Layout_Type.LOFT: 'loft'
    }
    for item in _layout:
        if item is not Layout_Type.NONE and item is not Layout_Type.FIVE_BEDROOM:
            data.append(switcher.get(item))
    return data


def validate_funnel_platform_data(_data: FunnelPlatformData):
    """
        @desc: this method will check for the _data and returns boolean, error dictionary and
        http response status code.
        @param: _data which contains the platform token and group id for Funnel.
        @return: a boolean, error dictionary and http response status code.
    """
    error = {}
    if DataValidation.isvalid_string(_data.apiToken) and DataValidation.isvalid_string(_data.communityID):
        return True, error, Tour_Integration_Constants.HTTP_GOOD_RESPONSE_CODE
    else:
        if not DataValidation.isvalid_string(_data.apiToken):
            error[Funnel_Constants.API_TOKEN] = 'Invalid Platform Token'
        if not DataValidation.isvalid_string(_data.communityID):
            error[Funnel_Constants.COMMUNITY_ID] = 'Invalid Community ID'
        return False, error, Tour_Integration_Constants.HTTP_BAD_RESPONSE_CODE


def convert_platformData(_data):
    """
        @desc: this method will check for the _data and returns the converted platform Token and
        group ID for Funnel.
        @param: _data which contains the platform token and group id for Funnel.
        @return: the converted platform Token and group ID for Funnel.
    """
    return FunnelPlatformData(_data[Funnel_Constants.COMMUNITY_ID],
                              _data[Funnel_Constants.API_TOKEN])


def get_token(token: str):
    """
        @desc: this method will check for the token and returns the basic http authorization token for Funnel.
        @param: token for the Funnel platform.
        @return: base64 encoded authorization token for Funnel.
    """
    # encode token into Base64
    message_bytes = token.encode(Funnel_Constants.ASCII)
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode(Funnel_Constants.ASCII)

    return {Funnel_Constants.AUTHORIZATION: 'Basic %s' % base64_message}


class Funnel_Platform(PlatformInterface):
    def get_tour_schedule_request_data(self, appointment_data: AppointmentData, platform_data: dict):
        """
             @desc: this method will check for the _data and returns the body, headers, params
             to schedule the tour appointment and the error.
             @param: _data which contains the appointment information like first name, last name
             and so on, platform specific information like token, group id and platform name.
             @return:the body, headers, params to schedule the tour appointment  and the error.
        """
        # creating funnel tour_scheduling API body.
        self.Error = {}
        self.Body = {}
        platform_Data = convert_platformData(platform_data)
        _isValid, _error, _responseCode = validate_funnel_platform_data(platform_Data)

        if _isValid:
            lead_source = 'WEBSITE'
            if appointment_data.get('source', None):
                lead_source = appointment_data.source.upper()
            else:
                lead_source = 'WEBSITE'
            appointment = DataValidation.serialize_object(Appointment(appointment_data.start))
            _person = DataValidation.serialize_object(
                Person(appointment_data.firstName, appointment_data.lastName,
                       appointment_data.email, appointment_data.phone))
            people = [_person]
            _layout = appointment_data.layout
            appointment_data.layout = get_funnel_room_layout(_layout)
            logging.info("lead_source {} {}".format(lead_source, get_platform_lead_source(lead_source)))
            client = DataValidation.serialize_object(
                Client(people, appointment_data.moveInDate, appointment_data.layout,
                       appointment_data.priceCeiling, get_platform_lead_source(lead_source), appointment_data.notes))
            _body = DataValidation.serialize_object(FunnelTourScheduleBodyClass(appointment, client))
            self.Body = _body
        else:
            self.Error = {Tour_Integration_Constants.RESPONSE_CODE: _responseCode,
                          Tour_Integration_Constants.RESPONSE_MESSAGE: _error}

        # creating funnel tour_scheduling API parameters.
        self.Params = {
            Funnel_Constants.GROUP_ID: platform_Data.communityID
        }

        # creating funnel tour_scheduling API header.
        self.Headers = get_token(platform_Data.apiToken)

        # returning funnel tour_scheduling API body, headers & parameters
        return self.Body, self.Headers, self.Params, self.Error

    def get_tour_availability_request_data(self, availability_data: TourAvailabilityData, platform_data: dict):
        """
            @desc: this method will check for the _data and returns the body, headers, to return the available tour
            appointment slots and the error.
            @param: _data which contains the appointment information like from date and to date and, platform specific
            information like token, group id and platform name.
            @return:the body, headers to get the available tour appointment slots and the error.
        """
        self.Error = {}
        self.Body = {}
        platform_Data = convert_platformData(platform_data)
        _isValid, _error, _responseCode = validate_funnel_platform_data(platform_Data)

        if _isValid:
            _body = DataValidation.serialize_object(
                FunnelTourAvailabilityClass(platform_Data.communityID, availability_data.fromDate,
                                            availability_data.toDate))
            self.Body = _body
        else:
            self.Error = {Tour_Integration_Constants.RESPONSE_CODE: _responseCode,
                          Tour_Integration_Constants.RESPONSE_MESSAGE: _error}

        # creating funnel tour_scheduling API header.
        self.Headers = get_token(platform_Data.apiToken)

        # returning funnel tour_scheduling API body, headers & parameters
        return self.Headers, self.Body, self.Error

    def format_tour_schedule_response(self, _data: dict):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from Funnel regarding confirmed tour appointment.
            @return: the formatted response and the http response status code.
        """
        response = {Tour_Integration_Constants.DATA: {}, Tour_Integration_Constants.ERROR: {}}
        response_Code = _data[Tour_Integration_Constants.RESPONSE_CODE]
        if response_Code == 200:
            _start = dateutil.parser.parse(
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE][Tour_Integration_Constants.DATA]['appointment'][
                    'start'])
            _end = dateutil.parser.parse(
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE][Tour_Integration_Constants.DATA]['appointment'][
                    'expiration_date'])
            response[Tour_Integration_Constants.DATA]['start'] = _start.strftime(
                Tour_Integration_Constants.DATETIME_FORMAT)
            response[Tour_Integration_Constants.DATA]['end'] = _end.strftime(Tour_Integration_Constants.DATETIME_FORMAT)
            response[Tour_Integration_Constants.DATA]['id'] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE][Tour_Integration_Constants.DATA]['appointment']['id']
        elif response_Code == 404:
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE][
                    'message']
        elif response_Code == 403:
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = 'Invalid Token'
        elif response_Code == 400:
            for key in _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['errors']['appointment'].keys():
                _message = ""
                for item in _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['errors']['appointment'][key]:
                    _message += str(item)
                response[Tour_Integration_Constants.ERROR][key] = _message
        else:
            response[Tour_Integration_Constants.ERROR] = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['errors']
        return response, response_Code

    def format_tour_availability_response(self, _data: dict):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from Funnel regarding available time slots for
            tour scheduling.
            @return: the formatted response and the http response status code.
        """
        response = {Tour_Integration_Constants.DATA: {}, Tour_Integration_Constants.ERROR: {}}
        response_Code = _data[Tour_Integration_Constants.RESPONSE_CODE]
        if response_Code == 200:
            list_Date = []
            for item in _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['available_times']:
                _date = dateutil.parser.parse(item)
                list_Date.append(_date.strftime(Tour_Integration_Constants.DATETIME_FORMAT))
            response[Tour_Integration_Constants.DATA][Tour_Integration_Constants.AVAILABLE_TIMES] = list_Date
        elif response_Code == 404:
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['message']
        elif response_Code == 403:
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = 'Invalid Token'
        elif response_Code == 400:
            response[Tour_Integration_Constants.ERROR] = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['errors']
        else:
            response[Tour_Integration_Constants.ERROR] = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['errors']
        return response, response_Code

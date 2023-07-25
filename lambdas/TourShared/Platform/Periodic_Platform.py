import datetime
import json
from TourShared.Model.Data_Model import BasePlatformData, HTTP_Request_Type, TourAvailabilityData, AppointmentData
from TourShared.Utilities.Data_Validation import DataValidation
from TourShared.Utilities.Tour_Constants import Tour_Integration_Constants
from TourShared.Interface.Platform_Interface import PlatformInterface
import jwt
import time
import requests
from typing import List


class PeriodicPlatformData(BasePlatformData):
    jwtIssuer: str
    jwtSubject: str
    reservationID: str
    jwtKey: str
    communityName: str
    platformFormID: str

    def __init__(self, _jwtIssuer=None, _jwtSubject=None, _jwtKey=None, _reservationID=None,
                 _communityName=None, platformFormID=None):
        self.reservationID = _reservationID
        self.jwtIssuer = _jwtIssuer
        self.jwtSubject = _jwtSubject
        self.jwtKey = _jwtKey
        self.communityName = _communityName
        self.platformFormID = platformFormID


class PeriodicBodyClass:
    jsonrpc: str
    method: str
    params: dict
    id: str

    def __init__(self, jsonrpc: str, method: str, params: dict, id: str) -> None:
        self.jsonrpc = jsonrpc
        self.method = method
        self.params = params
        self.id = id


class Periodic_Constants:
    GET_AVAILABILITY_METHOD = 'get_availability'
    GET_FORM_QUESTIONS_BY_FORM_METHOD = 'get_form_questions_by_form'
    CREATE_RESERVATION_METHOD = 'create_reservation'
    JSONRPC = '2.0'
    ID = '12345'
    AUTHORIZATION = 'Authorization'
    TIME_APPEND = ' 00:00:00'
    URL = 'https://admin.quextbooking.com/rpc'
    BOOKABLE = 'bookable'
    GET_AVAILABILITY_START = 'start'
    GET_AVAILABILITY_END = 'end'
    PROVIDER = 'provider'
    RESPONSES = 'responses'
    FORM_ID = 'form_id'
    TOKEN_BEARER = 'Bearer {}'
    FORM_RESPONSE_FIRSTNAME = 'First Name'
    FORM_RESPONSE_LASTNAME = 'Last Name'
    FORM_RESPONSE_EMAIL = 'Email'
    FORM_RESPONSE_PHONE = 'Phone'
    FORM_RESPONSE_MOVE_IN = 'Move in date'
    FORM_RESPONSE_BROKER = 'Broker Booked'
    FORM_RESPONSE_SOURCE = 'Discovery Source'
    FORM_RESPONSE_PRICE_CEILING = 'Price Ceiling'
    PLATFORM_FIELD_NOT_REQUIRED = 'Not_Required'


class Response:
    question_id: str
    value: str

    def __init__(self, question_id: str, value: str) -> None:
        self.question_id = question_id
        self.value = value


class Create_Reservation_Params:
    provider: str
    bookable: str
    whitelabel: str
    start: str
    end: str
    formresponses: List[dict]
    comments: str

    def __init__(self, provider: str, bookable: str, whitelabel: str, start: str, end: str, email: str,
                 first_name: str, last_name: str) -> None:
        self.provider = provider
        self.bookable = bookable
        self.whitelabel = whitelabel
        self.start = start
        self.end = end
        self.email = email
        self.first_name = first_name
        self.last_name = last_name


def send_http_request(request_Type: HTTP_Request_Type, _data: str, _auth: str, _header: dict):
    response = {}
    if request_Type == HTTP_Request_Type.GET:
        response = requests.get(Periodic_Constants.URL, data=_data, auth=_auth, headers=_header)
    else:
        response = requests.post(Periodic_Constants.URL, data=_data, auth=_auth, headers=_header)
    return response


def validate_periodic_platform_data(_data: PeriodicPlatformData):
    """
        @desc: this method will check for the _data and returns boolean, error dictionary and
        http response status code.
        @param: _data which contains the jwt key, provider name, issuer, subject, bookable and form is for Periodic.
        @return: a boolean, error dictionary and http response status code.
    """
    error = {}
    if DataValidation.isvalid_string(_data.jwtKey) and DataValidation.isvalid_string(
            _data.communityName) and DataValidation.isvalid_string(
        _data.jwtIssuer) and DataValidation.isvalid_string(
        _data.jwtSubject) and DataValidation.isvalid_string(_data.reservationID):
        if _data.platformFormID != Periodic_Constants.PLATFORM_FIELD_NOT_REQUIRED:
            return True, error, Tour_Integration_Constants.HTTP_GOOD_RESPONSE_CODE
        else:
            if DataValidation.isvalid_string(_data.platformFormID):
                return True, error, Tour_Integration_Constants.HTTP_GOOD_RESPONSE_CODE
            error['platformFormID'] = 'Invalid Platform Form ID'
            return False, error, Tour_Integration_Constants.HTTP_BAD_RESPONSE_CODE
    else:
        if not DataValidation.isvalid_string(_data.jwtKey):
            error['jwtKey'] = 'Invalid JWT Key'
        if not DataValidation.isvalid_string(_data.communityName):
            error['platformReservationName'] = 'Invalid Community Name'
        if not DataValidation.isvalid_string(_data.jwtIssuer):
            error['jwtIssuer'] = 'Invalid JWT  Issuer'
        if not DataValidation.isvalid_string(_data.jwtSubject):
            error['jwtSubject'] = 'Invalid JWT  Subject'
        if not DataValidation.isvalid_string(_data.reservationID):
            error['platformReservationID'] = 'Invalid Platform Reservation ID'
        if not DataValidation.isvalid_string(_data.platformFormID):
            error['platformFormID'] = 'Invalid Platform Form ID'
        return False, error, Tour_Integration_Constants.HTTP_BAD_RESPONSE_CODE


def get_token(issuer: str, subject: str, key: str):
    """
        @desc: this method will check for the issuer, subject , key and returns the basic http authorization token for
        Periodic.
        @param: issuer, subject and key for periodic platform.
        @return: jwt token for Periodic.
    """
    unix_Timestamp = int(time.time())
    return jwt.encode(
        {'iat': unix_Timestamp, 'iss': issuer, 'sub': subject},
        key, algorithm='HS256').decode('utf-8')


def convert_platformData(_data: dict):
    platForm_Data = PeriodicPlatformData(_data['jwtIssuer'], _data['jwtSubject'], _data['jwtKey'],
                                         _data['reservationID'], _data['communityName'],
                                         Periodic_Constants.PLATFORM_FIELD_NOT_REQUIRED)

    # Currently not using Form_ID
    if 'platform_Form_ID' in _data.keys():
        platForm_Data.platformFormID = _data['platform_Form_ID']
    return platForm_Data


def get_form_questions_by_form(form_ID: str, issuer: str, subject: str, key: str):
    data = {}
    body = DataValidation.serialize_object(
        PeriodicBodyClass(Periodic_Constants.JSONRPC, Periodic_Constants.GET_FORM_QUESTIONS_BY_FORM_METHOD,
                          {Periodic_Constants.FORM_ID: form_ID}, Periodic_Constants.ID))
    header = {Periodic_Constants.AUTHORIZATION: Periodic_Constants.TOKEN_BEARER.format(get_token(issuer, subject, key))}
    response = send_http_request(HTTP_Request_Type.POST, json.dumps(body), '', header)
    data[Tour_Integration_Constants.RESPONSE_CODE] = response.status_code
    data[Tour_Integration_Constants.RESPONSE_MESSAGE] = json.loads(response.text)
    return data


def isvalid_get_form_questions_by_form_response(_response: dict):
    isValid = False
    response = {}
    error = {Tour_Integration_Constants.DATA: {}, Tour_Integration_Constants.ERROR: {}}
    response_Code = _response[Tour_Integration_Constants.RESPONSE_CODE]
    if response_Code == 200:
        isValid = True
        dict_Question_ID = {}
        for item in _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['result']:
            key = item['name']
            dict_Question_ID[key] = item['id']
        response = dict_Question_ID
    elif response_Code == 404:
        error[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
            _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['error'][
                'message']
    elif response_Code == 401:
        message = _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
        error[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
            message.split("PERIODIC ERROR: ")[1]
    elif response_Code == 400:
        message = _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
        error[Tour_Integration_Constants.ERROR]['jwt'] = message.split("PERIODIC ERROR: ")[1]
    elif response_Code == 409:
        message = _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
        error[Tour_Integration_Constants.ERROR]['start'] = message.split("PERIODIC ERROR: ")[1]
    else:
        error = _response[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']
    return isValid, response, error, response_Code


class Periodic_Platform(PlatformInterface):
    def get_tour_schedule_request_data(self, appointment_data: AppointmentData, platform_data: dict):
        """
            @desc: this method will check for the _data and returns the body, headers, params
            to schedule the tour appointment and the error.
            @param: _data which contains the appointment information like first name, last name
            and so on, platform specific information like provider key, issuer, subject, provider name and platform name.
            @return:the body, headers, params to schedule the tour appointment  and the error.
        """
        # creating Periodic tour_scheduling API body.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}
        platform_Data = convert_platformData(platform_data)
        _isValidPlatformData, _errorPlatformDataResponse, _errorPlatformDataResponseCode = validate_periodic_platform_data(
            platform_Data)

        if _isValidPlatformData:
            _start = datetime.datetime.strptime(appointment_data.start,
                                                Tour_Integration_Constants.DATETIME_FORMAT)
            delta_Interval = datetime.timedelta(minutes=15)
            _end = (_start + delta_Interval).strftime(Tour_Integration_Constants.DATETIME_FORMAT)

            _body = DataValidation.serialize_object(
                PeriodicBodyClass(Periodic_Constants.JSONRPC, Periodic_Constants.CREATE_RESERVATION_METHOD,
                                  DataValidation.serialize_object(
                                      Create_Reservation_Params(platform_Data.communityName,
                                                                platform_Data.reservationID,
                                                                platform_Data.jwtIssuer,
                                                                appointment_data.start,
                                                                _end,
                                                                appointment_data.email,
                                                                appointment_data.firstName,
                                                                appointment_data.lastName)),
                                  Periodic_Constants.ID))
            self.Body = json.dumps(_body)
            # creating Periodic tour_scheduling API header.
            self.Headers = {Periodic_Constants.AUTHORIZATION: Periodic_Constants.TOKEN_BEARER.format(
                get_token(platform_Data.jwtIssuer, platform_Data.jwtSubject, platform_Data.jwtKey))}
        else:
            self.Error = {Tour_Integration_Constants.RESPONSE_CODE: _errorPlatformDataResponseCode,
                          Tour_Integration_Constants.RESPONSE_MESSAGE: _errorPlatformDataResponse}

            # returning Periodic tour_scheduling API body, headers & parameters
        return self.Body, self.Headers, self.Params, self.Error

    def get_tour_availability_request_data(self, availability_data: TourAvailabilityData, platform_data: dict):
        """
            @desc: this method will check for the _data and returns the body, headers, to return the available tour
            appointment slots and the error.
            @param: _data which contains the appointment information like from date and to date and, platform specific
            information like provider key, issuer, subject, provider name and platform name.
            @return: the body, headers to get the available tour appointment slots  and the error.
        """
        self.Error = {}
        self.Body = {}
        platform_Data = convert_platformData(platform_data)
        _isValid, _error, _responseCode = validate_periodic_platform_data(platform_Data)

        isValid_to_date = DataValidation.isvalid_date_format(availability_data.toDate)
        if not (isValid_to_date and len(availability_data.toDate) > 0):
            _isValid = False
            _error['toDate'] = 'Invalid To_Date Format'

        if _isValid:
            _fromDate = datetime.datetime.strptime(availability_data.fromDate, '%Y-%m-%d')
            _toDate = datetime.datetime.strptime(availability_data.toDate, '%Y-%m-%d')
            if _fromDate == _toDate:
                end_date = _toDate + datetime.timedelta(hours=24)
                availability_data.toDate = end_date.strftime('%Y-%m-%d')
            else:
                end_date = _toDate + datetime.timedelta(hours=24)
                availability_data.toDate = end_date.strftime('%Y-%m-%d')

            _body = DataValidation.serialize_object(
                PeriodicBodyClass(Periodic_Constants.JSONRPC, Periodic_Constants.GET_AVAILABILITY_METHOD,
                                  {Periodic_Constants.BOOKABLE: platform_Data.reservationID,
                                   Periodic_Constants.GET_AVAILABILITY_START:
                                       availability_data.fromDate + Periodic_Constants.TIME_APPEND,
                                   Periodic_Constants.GET_AVAILABILITY_END:
                                       availability_data.toDate + Periodic_Constants.TIME_APPEND,
                                   Periodic_Constants.PROVIDER: platform_Data.communityName},
                                  Periodic_Constants.ID))
            self.Body = _body
        else:
            self.Error = {Tour_Integration_Constants.RESPONSE_CODE: Tour_Integration_Constants.HTTP_BAD_RESPONSE_CODE,
                          Tour_Integration_Constants.RESPONSE_MESSAGE: _error}

        # creating Periodic tour_availability API header.
        self.Headers = {Periodic_Constants.AUTHORIZATION: Periodic_Constants.TOKEN_BEARER.format(
            get_token(platform_Data.jwtIssuer, platform_Data.jwtSubject, platform_Data.jwtKey))}

        # returning Periodic tour_scheduling API body, headers & parameters
        return self.Headers, self.Body, self.Error

    def format_tour_availability_response(self, _data: dict):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from periodic regarding available time slots for
            tour scheduling.
            @return: the formatted response and the http response status code.
        """
        response = {Tour_Integration_Constants.DATA: {}, Tour_Integration_Constants.ERROR: {}}
        response_Code = _data[Tour_Integration_Constants.RESPONSE_CODE]
        if response_Code == 200:
            list_date = []
            for item in _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['result']:
                if item['available']:
                    list_date.append(item['start'])

            if len(list_date) > 0:
                response[Tour_Integration_Constants.DATA][Tour_Integration_Constants.AVAILABLE_TIMES] = list_date
                response_Code = 200
            else:
                response[Tour_Integration_Constants.DATA][Tour_Integration_Constants.AVAILABLE_TIMES] = []
                response_Code = 400
        elif response_Code == 404:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                message.split("PERIODIC ERROR: ")
        elif response_Code == 401:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                message.split("PERIODIC ERROR: ")
        elif response_Code == 400:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR]['start'] = message.split("PERIODIC ERROR: ")
        else:
            response[Tour_Integration_Constants.ERROR] = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']
        return response, response_Code

    def format_tour_schedule_response(self, _data: dict):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from periodic regarding confirmed tour appointment.
            @return: the formatted response and the http response status code.
        """
        response = {Tour_Integration_Constants.DATA: {}, Tour_Integration_Constants.ERROR: {}}
        response_Code = _data[Tour_Integration_Constants.RESPONSE_CODE]
        if response_Code == 200:
            response[Tour_Integration_Constants.DATA]['start'] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['result']['start']
            response[Tour_Integration_Constants.DATA]['end'] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['result']['end']
            response[Tour_Integration_Constants.DATA]['id'] = \
                _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['result']['id']
        elif response_Code == 404:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                message.split("PERIODIC ERROR: ")
        elif response_Code == 400:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR]['start'] = message.split("PERIODIC ERROR: ")
        elif response_Code == 409:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR]['start'] = message.split("PERIODIC ERROR: ")
        elif response_Code == 401:
            message = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']['message']
            response[Tour_Integration_Constants.ERROR][Tour_Integration_Constants.PLATFORM_DATA] = \
                message.split("PERIODIC ERROR: ")
        else:
            response[Tour_Integration_Constants.ERROR] = _data[Tour_Integration_Constants.RESPONSE_MESSAGE]['error']
        return response, response_Code

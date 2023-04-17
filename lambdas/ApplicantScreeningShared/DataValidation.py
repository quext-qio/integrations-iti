import datetime
import logging
import re
from enum import Enum
from typing import List

from cerberus import Validator


class BasePlatformData:
    communityUUID: str
    customerUUID: str


class BaseApplicantItem:
    referenceId: str
    firstName: str
    middleName: str
    lastName: str
    streetAddress: str
    city: str
    state: str
    postalCode: str

    def __init__(self, _referenceId, _firstName, _middleName, _lastName, _streetAddress, _city, _state, _postalCode):
        self.referenceId = _referenceId
        self.firstName = _firstName
        self.middleName = _middleName
        self.lastName = _lastName
        self.streetAddress = _streetAddress
        self.city = _city
        self.state = _state
        self.postalCode = _postalCode


class BaseApplicantData:
    applicant: []

    def __init__(self):
        self.applicant = []


class ScreeningResult:
    applicationStatus: str
    creditStatus: str
    criminalStatus: str
    evictionStatus: str

    def __init__(self):
        self.applicationStatus = ''
        self.creditStatus = ''
        self.criminalStatus = ''
        self.evictionStatus = ''


class BaseData:
    referenceId: str
    applicationNumber: str
    timeStamp: str
    applicants: BaseApplicantData
    screeningResult: ScreeningResult
    screeningReport: str

    def __init__(self, _timeStamp):
        self.referenceId = ''
        self.applicationNumber = ''
        self.timeStamp = _timeStamp
        self.applicants = BaseApplicantData()
        self.screeningResult = ScreeningResult()
        self.screeningReport = ''


class ScreeningErrorType(Enum):
    NONE = ''
    VALIDATION_ERROR = 'ValidationError'
    SYSTEM_ERROR = 'SystemError'
    AUTHENTICATION_ERROR = 'AuthenticationError'


class BaseErrorItem:
    Field: str
    Reason: str

    def __init__(self, _field, _reason):
        self.Field = _field
        self.Reason = _reason


class BaseError:
    ErrorType: ScreeningErrorType
    ErrorMessage: str
    InvalidParameter: []

    def __init__(self, _type, _params):
        self.ErrorType = _type
        self.ErrorMessage = ''
        self.InvalidParameter = _params


class BaseApplicantScreeningResponse:
    data: BaseData
    error: BaseError

    def __init__(self):
        self.data = BaseData('')
        self.error = BaseError(ScreeningErrorType.NONE.value, [])


class Address:
    streetAddress: str
    unitNumber: str
    city: str
    state: str
    postalCode: str
    country: str


class BaseApplicant:
    firstName: str
    middleName: str
    lastName: str
    suffix: str
    birthDate: str
    email: str
    address: Address
    ssn: str
    employmentIncome: str
    employmentIncomePeriod: str
    otherIncome: str
    otherIncomePeriod: str
    assetsValue: str
    employmentStatus: str
    criminal: str
    eviction: str
    credit: str


class BaseApplicationScreeningData:
    rentAmount: str
    depositAmount: str
    leaseTerm: str
    marketingSource: str
    applicants: List[BaseApplicant]


class BaseApplicationRetrievalData:
    applicationNumber: str
    referenceId: str


class HTTPRequestType(Enum):
    GET = 0
    POST = 1


class HTTPRequest(Enum):
    GET = 'GET'
    POST = 'POST'


class ApplicantScreeningPayload:
    applicationData: BaseApplicationScreeningData
    platformData: BasePlatformData


class ApplicantRetrievalPayload:
    applicationData: BaseApplicationRetrievalData
    platformData: BasePlatformData


class Schema(Enum):
    NONE = 0,
    CREATE_APPLICATION = 1,
    PLATFORM_DATA = 2,
    ADDRESS = 3,
    RETRIEVE_APPLICATION = 4


usStateAbbrev = {'ALABAMA': 'AL', 'ALASKA': 'AK', 'ARIZONA': 'AZ', 'ARKANSAS': 'AR', 'CALIFORNIA': 'CA',
                 'COLORADO': 'CO', 'CONNECTICUT': 'CT', 'DELAWARE': 'DE', 'FLORIDA': 'FL', 'GEORGIA': 'GA',
                 'HAWAII': 'HI', 'IDAHO': 'ID', 'ILLINOIS': 'IL', 'INDIANA': 'IN', 'IOWA': 'IA', 'KANSAS': 'KS',
                 'KENTUCKY': 'KY', 'LOUISIANA': 'LA', 'MAINE': 'ME', 'MARYLAND': 'MD', 'MASSACHUSETTS': 'MA',
                 'MICHIGAN': 'MI', 'MINNESOTA': 'MN', 'MISSISSIPPI': 'MS', 'MISSOURI': 'MO', 'MONTANA': 'MT',
                 'NEBRASKA': 'NE', 'NEVADA': 'NV', 'NEW HAMPSHIRE': 'NH', 'NEW JERSEY': 'NJ', 'NEW MEXICO': 'NM',
                 'NEW YORK': 'NY', 'NORTH CAROLINA': 'NC', 'NORTH DAKOTA': 'ND', 'OHIO': 'OH', 'OKLAHOMA': 'OK',
                 'OREGON': 'OR', 'PENNSYLVANIA': 'PA', 'RHODE ISLAND': 'RI', 'SOUTH CAROLINA': 'SC',
                 'SOUTH DAKOTA': 'SD', 'TENNESSEE': 'TN', 'TEXAS': 'TX', 'UTAH': 'UT', 'VERMONT': 'VT',
                 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WEST VIRGINIA': 'WV', 'WISCONSIN': 'WI', 'WYOMING': 'WY',
                 'DISTRICT OF COLUMBIA': 'DC', 'NORTHERN MARIANA ISLANDS': 'MP', 'PALAU': 'PW',
                 'PUERTO RICO': 'PR', 'VIRGIN ISLANDS': 'VI'}


class ValidationConstants:
    UUID_REGEX = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    CHARACTER_REGEX = "^[A-Za-z -]+$"
    CITY_REGEX = "^[A-Za-z '-]+$"
    EMAIL_REGEX = "(^(^\"([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~\.]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\")|(^\"\s\")|(^([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~\.]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+))@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,7})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,7})?)$"
    PHONE_REGEX = "^(?:(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$"
    STREET_ADDRESS_REGEX = "^[0-9A-Za-z -]+$"
    US_STATES = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut",
                 "District ", "of Columbia", "Delaware", "Florida", "Georgia", "Guam", "Hawaii", "Iowa", "Idaho",
                 "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine",
                 "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota",
                 "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma",
                 "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
                 "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia",
                 "Wyoming"]
    COUNTRY = ['USA', '']
    SUFFIX = ['JR', 'SR', 'I', 'II', 'III', 'IV']
    POSTAL_CODE_REGEX = "^[0-9]{5}(?:-[0-9]{4})?$"
    TIME_REGEX = "^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$"
    AMOUNT_REGEX = "^[0-9]\d*(((,\d{3}){1})?(\.\d{0,2})?)$"
    NAME_REGEX = "^[A-Za-z '.-]+$"
    DATE_REGEX = "^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))$"
    SSN_REGEX = "^\d{9}$"
    BOOLEAN = ['True', 'False', 'true', 'false']


class ApplicantScreeningConstants:
    RESPONSE_CODE = 'responseCode'
    RESPONSE_MESSAGE = 'responseMessage'
    COMMUNITY_UUID = 'communityUUID'
    CUSTOMER_UUID = 'customerUUID'
    PURPOSE = 'purpose'
    RESIDENT_SCREENING_PURPOSE = 'applicantScreening'
    PLATFORM_FETCH_CHANNEL = 'Platform_Outgoing_Channel'
    HTTP_BAD_RESPONSE_CODE = 400
    HTTP_INTERNAL_SERVICE_ERROR = 500
    HTTP_GOOD_RESPONSE_CODE = 200
    ERROR = 'errors'
    DATA = 'data'
    PLATFORM_DATA = 'platformData'
    APPLICANT_SCREENING_REQUEST_METHOD = 'getApplicantScreeningRequestData'
    APPLICANT_RETRIEVAL_REQUEST_METHOD = 'getApplicantRetrievalRequestData'
    FORMAT_APPLICANT_SCREENING_RESPONSE_METHOD = 'formatCreateApplicationResponse'
    REFERENCE_ID = 'referenceId'
    APPLICATION_NUMBER = 'applicationNumber'
    BAD_REQUEST_MESSAGE = 'Internal Server Error'
    BACKGROUND_SCREENING_MAX_ITERATIONS = 10


class DataValidation:

    @staticmethod
    def serialize_object(obj):
        if isinstance(obj, datetime.date):
            serial = obj.isoformat()
            return serial
        return obj.__dict__

    @staticmethod
    def validatePlatformResponse(_responseCode):
        _isValid = False
        _error = BaseApplicantScreeningResponse()

        if _responseCode == 200:
            _isValid = True
        elif _responseCode == 404:
            _errorItem = BaseErrorItem(ApplicantScreeningConstants.PLATFORM_DATA, 'Invalid Platform Data')
            _error.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        elif _responseCode == 400:
            _errorItem = BaseErrorItem(ApplicantScreeningConstants.PLATFORM_DATA, 'Invalid Platform Data')
            _error.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        return _isValid, _error

    @staticmethod
    def validateDateFormat(_date: str):
        regex_Date = '^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))$'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_date) is not None:
            return True
        return False

    @staticmethod
    def validateUUIDFormat(_uuid: str):
        regex_Date = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_uuid) is not None:
            return True
        return False

    @staticmethod
    def createApplicationScreeningResponse(_baseResponse: BaseApplicantScreeningResponse, _baseData: BaseData,
                                           _baseApplicantData: BaseApplicantData, _screeningResult: ScreeningResult,
                                           _baseError: BaseError):
        _baseResponse.data.applicants = DataValidation.serialize_object(_baseApplicantData)
        _baseResponse.data.screeningResult = DataValidation.serialize_object(_screeningResult)
        _baseResponse.data = DataValidation.serialize_object(_baseData)
        _baseResponse.error = DataValidation.serialize_object(_baseError)
        return DataValidation.serialize_object(_baseResponse)

    @staticmethod
    def formatError(obj, key, responseObj, duplicateKey):
        if isinstance(obj, dict):
            return {k: DataValidation.formatError(v, k, responseObj, duplicateKey) for k, v in obj.items()}
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
            if key not in duplicateKey:
                responseObj.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
                if "regex" in obj[0] or "missing" in obj[0]:
                    duplicateKey.append(key)
                    _errorItem = BaseErrorItem(key, 'invalid ' + key)
                    responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
                    return obj[0]
                else:
                    _errorItem = BaseErrorItem(key, obj[0])
                    responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
                    duplicateKey.append(key)
                    return obj[0]
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], dict):
            return DataValidation.formatError(obj[0], None, responseObj, duplicateKey)
        elif isinstance(obj, list) and len(obj) > 1:
            return {k: DataValidation.formatError(v, k, responseObj, duplicateKey) for k, v in obj}

    @staticmethod
    def schema(_schemaType: Schema, _data):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        v = Validator()
        isValid = v.validate(_data, Validation_Schema[_schemaType])
        responseObj = BaseApplicantScreeningResponse()
        DataValidation.formatError(v.errors, None, responseObj, [])
        return isValid, DataValidation.createApplicationScreeningResponse(responseObj, responseObj.data,
                                                                          responseObj.data.applicants,
                                                                          responseObj.data.screeningResult,
                                                                          responseObj.error)

    @staticmethod
    def getPlatformRequestData(_data: BasePlatformData, _purpose: str):
        error = {}
        param = {}
        _isValid, _error = DataValidation.schema(Schema.PLATFORM_DATA, _data)
        if _isValid:
            param = {
                ApplicantScreeningConstants.COMMUNITY_UUID: _data.communityUUID,
                ApplicantScreeningConstants.CUSTOMER_UUID: _data.customerUUID,
                ApplicantScreeningConstants.PURPOSE: _purpose
            }
        else:
            error = {ApplicantScreeningConstants.RESPONSE_CODE: ApplicantScreeningConstants.HTTP_BAD_RESPONSE_CODE,
                     ApplicantScreeningConstants.RESPONSE_MESSAGE: _error}
        return param, error

    @staticmethod
    def validateBaseApplicationScreeningData(_data: BaseApplicationScreeningData):
        _isValid, _error = DataValidation.schema(Schema.CREATE_APPLICATION, _data)
        return _isValid, _error

    @staticmethod
    def validateBaseApplicationRetrievalData(_data: BaseApplicationRetrievalData):
        _isValid, _error = DataValidation.schema(Schema.RETRIEVE_APPLICATION, _data)
        return _isValid, _error


Validation_Schema = {
    Schema.NONE: None,
    Schema.PLATFORM_DATA: {
        'communityUUID': {'required': True,
                          'type': 'string',
                          'regex': ValidationConstants.UUID_REGEX},
        'customerUUID': {'required': True,
                         'type': 'string',
                         'regex': ValidationConstants.UUID_REGEX}
    },
    Schema.CREATE_APPLICATION: {
        'rentAmount': {'required': True,
                       'type': 'string',
                       'regex': ValidationConstants.AMOUNT_REGEX},
        'depositAmount': {
            'type': 'string',
            'regex': ValidationConstants.AMOUNT_REGEX,
            'empty': True},
        'leaseTerm': {'required': True,
                      'type': 'string'},
        'marketingSource': {'required': True,
                            'type': 'string'},
        'applicants': {'required': True,
                       'type': 'list',
                       'schema': {
                           'type': 'dict',
                           'schema': {
                               'firstName': {
                                   'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.NAME_REGEX
                               },
                               'middleName': {
                                   'type': 'string',
                                   'regex': ValidationConstants.NAME_REGEX,
                                   'empty': True
                               },
                               'lastName': {
                                   'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.NAME_REGEX
                               },
                               'suffix': {
                                   'type': 'string',
                                   'allowed': ValidationConstants.SUFFIX,
                                   'empty': True
                               },
                               'birthDate': {
                                   'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.DATE_REGEX
                               },
                               'email': {
                                   'empty': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.EMAIL_REGEX
                               },
                               'address': {
                                   'required': True,
                                   'type': 'dict',
                                   'schema': {'streetAddress': {'required': True,
                                                                'type': 'string',
                                                                'regex': ValidationConstants.STREET_ADDRESS_REGEX},
                                              'unitNumber': {
                                                  'type': 'string',
                                                  'empty': True
                                              },
                                              'city': {'required': True,
                                                       'type': 'string',
                                                       'regex': ValidationConstants.CITY_REGEX},
                                              'state': {'required': True,
                                                        'type': 'string',
                                                        'allowed': ValidationConstants.US_STATES},
                                              'country': {'empty': True,
                                                          'type': 'string',
                                                          'allowed': ValidationConstants.COUNTRY},
                                              'postalCode': {'required': True,
                                                             'type': 'string',
                                                             'regex': ValidationConstants.POSTAL_CODE_REGEX},
                                              }
                               },
                               'ssn': {
                                   'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.SSN_REGEX
                               },
                               'employmentIncome': {
                                   'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.AMOUNT_REGEX,
                                   'empty': True
                               },
                               'employmentIncomePeriod': {
                                   'required': True,
                                   'type': 'string',
                                   'empty': True
                               },
                               'otherIncome': {
                                   'type': 'string',
                                   'regex': ValidationConstants.AMOUNT_REGEX,
                                   'empty': True
                               },
                               'otherIncomePeriod': {
                                   'type': 'string',
                                   'empty': True
                               },
                               'assetsValue': {
                                   'type': 'string',
                                   'regex': ValidationConstants.AMOUNT_REGEX,
                                   'empty': True
                               },
                               'employmentStatus': {
                                   'required': True,
                                   'type': 'string'
                               },
                               'criminal': {
                                   'required': True,
                                   'type': 'string',
                                   'allowed': ValidationConstants.BOOLEAN,
                                   'empty': True
                               },
                               'eviction': {
                                   'required': True,
                                   'type': 'string',
                                   'allowed': ValidationConstants.BOOLEAN,
                                   'empty': True
                               },
                               'credit': {
                                   'required': True,
                                   'type': 'string',
                                   'allowed': ValidationConstants.BOOLEAN,
                                   'empty': True
                               }
                           }
                       }
                       }
    },
    Schema.RETRIEVE_APPLICATION: {

        'applicationNumber': {'type': 'string',
                              'required': True},
        'referenceId': {
            'type': 'string',
            'empty': True
        }
    }

}
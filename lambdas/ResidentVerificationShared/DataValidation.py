import datetime
import re
from enum import Enum
from typing import List

from cerberus import Validator


class BasePlatformData:
    communityUUID: str
    customerUUID: str


class Address:
    streetAddress: str
    city: str
    state: str
    postalCode: str
    country: str
    addressType: str


class BaseApplicantData:
    firstName: str
    middleName: str
    lastName: str
    phone: str
    email: str
    ssn: str
    birthDate: str
    address: Address


class SecurityQuestion:
    questionKey: str
    answerKey: str


class BaseIdentityEvaluationData:
    referenceNumber: str
    securityQuestions: List[SecurityQuestion]


class IdentityVerificationPayload:
    applicantData: BaseApplicantData
    platformData: BasePlatformData


class IdentityEvaluationPayload:
    evaluationData: BaseIdentityEvaluationData
    platformData: BasePlatformData


class HTTPRequestType(Enum):
    GET = 0
    POST = 1


class VerificationStatusType(Enum):
    NONE = ''
    SUCCESS = 'Success'
    FAIL = 'Fail'


class Schema(Enum):
    NONE = 0,
    IDENTITY_VERIFICATION = 1,
    PLATFORM_DATA = 2,
    ADDRESS = 3,
    IDENTITY_EVALUATION = 4


class VerificationErrorType(Enum):
    NONE = ''
    VALIDATION_ERROR = 'ValidationError'
    SYSTEM_ERROR = 'SystemError'
    VERIFICATION_ERROR = 'VerificationError'
    AUTHENTICATION_ERROR = 'AuthenticationError'


class RiskType(Enum):
    NONE = ''
    LOW = 'Low'
    MODERATE = 'Moderate'
    HIGH = 'High'


class BaseVerificationQuestion:
    Question: str
    SelectedResponse: str


class BaseErrorItem:
    Field: str
    Reason: str

    def __init__(self, _field, _reason):
        self.Field = _field
        self.Reason = _reason


class BaseError:
    ErrorType: VerificationErrorType
    InvalidParameter: []

    def __init__(self, _type, _params):
        self.ErrorType = _type
        self.InvalidParameter = _params


class BaseData:
    ReferenceNumber: str
    VerificationStatus: VerificationStatusType
    VerificationDetails: []
    ApplicationNumber: str
    PotentialRisk: RiskType
    SecurityQuestions: []

    def __init__(self, _applicationNumber, _risk, _securityQuestion):
        self.ReferenceNumber = ''
        self.VerificationStatus = VerificationStatusType.NONE.value
        self.VerificationDetails = []
        self.ApplicationNumber = _applicationNumber
        self.PotentialRisk = _risk
        self.SecurityQuestions = _securityQuestion


class SecurityAnswerItem:
    AnswerKey: str
    AnswerDescription: str

    def __init__(self, _answerKey, _description):
        self.AnswerKey = _answerKey
        self.AnswerDescription = _description


class SecurityQuestionItem:
    QuestionKey: str
    QuestionDescription: str
    Answers: []

    def __init__(self, _key, _description, _answer):
        self.QuestionKey = _key
        self.QuestionDescription = _description
        self.Answers = _answer


class BaseIdentityVerificationResponse:
    data: BaseData
    error: BaseError

    def __init__(self):
        self.data = BaseData('', RiskType.NONE.value, [])
        self.error = BaseError(VerificationErrorType.NONE.value, [])


class BaseEvaluationData:
    ReferenceNumber: str
    VerificationStatus: VerificationStatusType
    VerificationDetails: []
    ApplicationNumber: str
    PotentialRisk: str

    def __init__(self, _applicationNumber, _risk):
        self.ReferenceNumber = ''
        self.VerificationStatus = VerificationStatusType.NONE.value
        self.VerificationDetails = []
        self.ApplicationNumber = _applicationNumber
        self.PotentialRisk = _risk


class BaseIdentityEvaluationResponse:
    data: BaseEvaluationData
    error: BaseError

    def __init__(self):
        self.data = BaseEvaluationData('', RiskType.NONE.value)
        self.error = BaseError(VerificationErrorType.NONE.value, [])


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
    POSTAL_CODE_REGEX = "^[0-9]{5}(?:-[0-9]{4})?$"
    ADDRESS_TYPE = ['Current', 'Previous']
    TIME_REGEX = "^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$"
    AMOUNT_REGEX = "/^\$?[0-9]+(\.[0-9][0-9])?$/"
    NAME_REGEX = "^[A-Za-z '.-]+$"
    DATE_REGEX = "^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))$"
    SSN_REGEX = "^\d{9}$"
    BOOLEAN = ['True', 'False', 'true', 'false']


class ResidentVerificationConstants:
    RESPONSE_CODE = 'responseCode'
    RESPONSE_MESSAGE = 'responseMessage'
    COMMUNITY_UUID = 'communityUUID'
    CUSTOMER_UUID = 'customerUUID'
    PURPOSE = 'purpose'
    IDENTITY_VERIFICATION_PURPOSE = 'identityVerification'
    PLATFORM_FETCH_CHANNEL = 'Platform_Outgoing_Channel'
    HTTP_BAD_RESPONSE_CODE = 400
    HTTP_GOOD_RESPONSE_CODE = 200
    ERROR = 'errors'
    DATA = 'data'
    FIRST_NAME = 'firstName'
    MIDDLE_NAME = 'middleName'
    LAST_NAME = 'lastName'
    PHONE = 'phone'
    EMAIL = 'email'
    SSN = 'ssn'
    BIRTH_DATE = 'birthDate'
    ADDRESS = 'address'
    ADDRESS_TYPE = 'addressType'
    STREET_ADDRESS = 'streetAddress'
    CITY = 'city'
    STATE = 'state'
    POSTAL_CODE = 'postalCode'
    COUNTRY = 'country'
    PLATFORM_DATA = 'platformData'
    RESIDENT_VERIFICATION_REQUEST_METHOD = 'getIdentityVerificationRequestData'
    RESIDENT_EVALUATION_REQUEST_METHOD = 'getIdentityEvaluationRequestData'
    FORMAT_RESIDENT_VERIFICATION_RESPONSE_METHOD = 'formatIdentityVerificationResponse'
    FORMAT_RESIDENT_EVALUATION_RESPONSE_METHOD = 'formatIdentityEvaluationResponse'
    QUESTION = 'questionKey'
    ANSWER = 'answerKey'
    SECURITY_QUESTIONS = 'securityQuestions'
    REFERENCE_NUMBER = 'referenceNumber'
    EVALUATION_DATA = 'evaluationData'
    BAD_REQUEST_MESSAGE = 'Internal Server Error'


class DataValidation:

    @staticmethod
    def validateStringField(_field: str):
        if type(_field) is str and (len(_field) > 0):
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
    def serialize_object(obj):
        if isinstance(obj, datetime.date):
            serial = obj.isoformat()
            return serial
        return obj.__dict__

    @staticmethod
    def validatePlatformData(_data):

        if ResidentVerificationConstants.EVALUATION_DATA in _data:
            responseObj = BaseIdentityEvaluationResponse()
            isValid, responseObj = DataValidation.schema(Schema.PLATFORM_DATA, _data.platformData, responseObj)
            if not isValid:
                responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value.value
            return isValid, DataValidation.createEvaluationResponse(responseObj, responseObj.data,
                                                                    responseObj.error)
        else:
            responseObj = BaseIdentityVerificationResponse()
            isValid, responseObj = DataValidation.schema(Schema.PLATFORM_DATA, _data.platformData, responseObj)
            if not isValid:
                responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
            return isValid, DataValidation.createVerificationResponse(responseObj, responseObj.data,
                                                                      responseObj.error)

    @staticmethod
    def createVerificationResponse(_baseVerificationResponse: BaseIdentityVerificationResponse,
                                   _baseData: BaseData, _baseError: BaseError):
        _baseVerificationResponse.data = DataValidation.serialize_object(_baseData)
        _baseVerificationResponse.error = DataValidation.serialize_object(_baseError)
        return DataValidation.serialize_object(_baseVerificationResponse)

    @staticmethod
    def createEvaluationResponse(_baseEvaluationResponse: BaseIdentityEvaluationResponse,
                                 _baseData: BaseEvaluationData, _baseError: BaseError):
        _baseEvaluationResponse.data = DataValidation.serialize_object(_baseData)
        _baseEvaluationResponse.error = DataValidation.serialize_object(_baseError)
        return DataValidation.serialize_object(_baseEvaluationResponse)

    @staticmethod
    def validatePlatformResponse(_responseCode):
        _isValid = False
        _error = {}

        if _responseCode == 200:
            _isValid = True
        elif _responseCode == 404:
            _error[ResidentVerificationConstants.PLATFORM_DATA] = 'Invalid Platform Data'
        elif _responseCode == 400:
            _error[ResidentVerificationConstants.PLATFORM_DATA] = 'Invalid Platform Data'
        return _isValid, _error

    @staticmethod
    def formatError(obj, key, responseObj, duplicateKey):
        if isinstance(obj, dict):
            return {k: DataValidation.formatError(v, k, responseObj, duplicateKey) for k, v in obj.items()}
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
            if key not in duplicateKey:
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
    def schema(_schemaType: Schema, _data: dict, responseObj):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        v = Validator()
        isValid = v.validate(_data, Validation_Schema[_schemaType])
        DataValidation.formatError(v.errors, None, responseObj, [])
        return isValid, responseObj

    @staticmethod
    def getPlatformRequestData(_data, _purpose: str):
        error = {}
        param = {}
        _isValid, _error = DataValidation.validatePlatformData(_data)
        if _isValid:
            param = {
                ResidentVerificationConstants.COMMUNITY_UUID: _data.platformData.communityUUID,
                ResidentVerificationConstants.CUSTOMER_UUID: _data.platformData.customerUUID,
                ResidentVerificationConstants.PURPOSE: _purpose
            }
        else:
            error = {ResidentVerificationConstants.RESPONSE_CODE: ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE,
                     ResidentVerificationConstants.RESPONSE_MESSAGE: _error}
        return param, error

    @staticmethod
    def validateBaseResidentData(_data):
        responseObj = BaseIdentityVerificationResponse()
        isValid, responseObj = DataValidation.schema(Schema.IDENTITY_VERIFICATION, _data.applicantData, responseObj)
        if not isValid:
            responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
        return isValid, DataValidation.createVerificationResponse(responseObj, responseObj.data,
                                                                  responseObj.error)

    @staticmethod
    def validateBaseIdentityEvaluationData(_data):
        responseObj = BaseIdentityEvaluationResponse()
        isValid, responseObj = DataValidation.schema(Schema.IDENTITY_EVALUATION, _data.evaluationData, responseObj)
        if not isValid:
            responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
        return isValid, DataValidation.createEvaluationResponse(responseObj, responseObj.data,
                                                                responseObj.error)


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
    Schema.IDENTITY_VERIFICATION: {
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
        'birthDate': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.DATE_REGEX
        },
        'ssn': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.SSN_REGEX
        },
        'phone': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.PHONE_REGEX
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
                       'city': {'required': True,
                                'type': 'string',
                                'regex': ValidationConstants.CITY_REGEX},
                       'state': {'required': True,
                                 'type': 'string',
                                 'allowed': ValidationConstants.US_STATES},
                       'country': {'required': True,
                                   'type': 'string',
                                   'allowed': ValidationConstants.COUNTRY},
                       'postalCode': {'required': True,
                                      'type': 'string',
                                      'regex': ValidationConstants.POSTAL_CODE_REGEX},
                       'addressType': {
                           'required': True,
                           'type': 'string',
                           'allowed': ValidationConstants.ADDRESS_TYPE
                       }
                       }
        }

    },
    Schema.IDENTITY_EVALUATION: {
        'referenceNumber': {'required': True,
                            'type': 'string'},
        'securityQuestions': {
            'required': True,
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'questionKey': {
                        'required': True,
                        'type': 'string'
                    },
                    'answerKey': {
                        'required': True,
                        'type': 'string'
                    }
                }
            }
        }
    }
}
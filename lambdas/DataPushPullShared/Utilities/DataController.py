import base64
import json
import logging
import re
from enum import Enum
import pycountry
from cerberus import Validator
from datetime import datetime

from DataPushPullShared.Model.CommonStructure import CommonStructure
from DataPushPullShared.Utilities.Convert import Convert
from VendorShared.Model.ServiceRequest import ServiceRequest
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto import Random
import hashlib

class Datasource(Enum):
    NONE = 0
    NEWCO_DEV = 1
    NEWCO_PROD = 2


class Schema(Enum):
    NONE = 0
    PLATFORM_DATA = 1,
    CUSTOMER_UUID = 2,
    COMMUNITY = 5,
    RESIDENTS = 6,
    PROSPECTS = 7,
    TRANSACTIONS = 8,
    CUSTOMER_EVENTS = 9,
    TOUR_AVAILABILITY = 10
    UNIT_AVAILABLE_PRICE_PAYLOAD = 11
    REAL_PAGE_GUESTCARD_PAYLOAD = 12
    GUEST_CARDS = 13
    REAL_PAGE_GET_AGENT_APPOINTMENT_TIME = 14
    TOUR_SCHEDULE_PAYLOAD = 15
    ENTRATA_GUESTCARD_PAYLOAD = 16
    FUNNEL_GUESTCARD_PAYLOAD = 17
    UNIT_AVAILABILITY = 18

class BaseUnitAvailabilityResponse:

    def __init__(self):
        self.data = {}
        self.error = {}


class QuextIntegrationConstants:
    INPUT = 'input'
    OUTPUT = 'output'
    OPERATION = 'operation'
    PLATFORM_FETCH_CHANNEL = 'Platform_Outgoing_Channel'
    UNIT_AVAILABILITY_PURPOSE = 'unitAvailability'
    RESPONSE_CODE = 'responseCode'
    RESPONSE_MESSAGE = 'responseMessage'
    HTTP_BAD_RESPONSE_CODE = 400
    HTTP_GOOD_RESPONSE_CODE = 200
    PLATFORM_DATA = 'platformData'
    ACTION = 'action'
    SUCCESS = 'success'
    DATA = 'data'
    ERROR = 'error'
    CODE = 'code'
    COMMUNITY_UUID = 'communityUUID'
    CUSTOMER_UUID = 'customerUUID'
    PURPOSE = 'purpose'
    MESSAGE = 'message'
    UNIT_AVAILABILITY_METHOD = 'getRequestData'
    FORMAT_UNIT_AVAILABILITY_RESPONSE_METHOD = 'formatResponse'
    CREATED_AFTER = "createdAfter"
    UPDATED_AFTER = "updatedAfter"
    CREATED_BEFORE = "createdBefore"
    UPDATED_BEFORE = "updatedBefore"
    RENTDYNAMICS_ERROR_FOR_DATE = "No Records Found for the input time range"
    #PAGINATION RESPONSE CONSTANTS
    TOTAL_PAGES = "total_pages"
    CURRENT_PAGE = "current_page"
    PAGE = "page"
    DEFAULT_LIMIT = 50
    DIGITALHUMAN = "digital human"
    RESULT = "result"

class CommunityConstants:
    COMMUNITY = 'community_details'
    COMMUNITY_AFTER_DEPOSITION = 'community_details_after_deposition_date'
    COMMUNITY_BEFORE_DEPOSITION = 'community_details_before_deposition_date'
    COMMUNITY_CUSTOMER_ID = 'community_details_by_acct'
    COMMUNITY_ID = 'community_details_by_id'
    COMMUNITY_OPERATION_ID = 'community_id'


class UnitConstants:
    UNIT = 'units'
    UNIT_COMMUNITY_ID = 'units_by_community'
    UNIT_ID = 'units_by_id'


class AmenityConstants:
    AMENITY_COMMUNITY_ID = 'unit_amenities_by_community'
    AMENITY_UNIT_ID = 'unit_amenities_by_unit'


us_state_abbrev = {
    'AL': 'ALABAMA',
    'AK': 'ALASKA',
    'AZ': 'ARIZONA',
    'AR': 'ARKANSAS',
    'CA': 'CALIFORNIA',
    'CO': 'COLORADO',
    'CT': 'CONNECTICUT',
    'DE': 'DELAWARE',
    'FL': 'FLORIDA',
    'GA': 'GEORGIA',
    'HI': 'HAWAII',
    'ID': 'IDAHO',
    'IL': 'ILLINOIS',
    'IN': 'INDIANA',
    'IA': 'IOWA',
    'KS': 'KANSAS',
    'KY': 'KENTUCKY',
    'LA': 'LOUISIANA',
    'ME': 'MAINE',
    'MD': 'MARYLAND',
    'MA': 'MASSACHUSETTS',
    'MI': 'MICHIGAN',
    'MN': 'MINNESOTA',
    'MS': 'MISSISSIPPI',
    'MO': 'MISSOURI',
    'MT': 'MONTANA',
    'NE': 'NEBRASKA',
    'NV': 'NEVADA',
    'NH': 'NEW HAMPSHIRE',
    'NJ': 'NEW JERSEY',
    'NM': 'NEW MEXICO',
    'NY': 'NEw YORK',
    'NC': 'NORTH CAROLINA',
    'ND': 'NORTH DAKOTA',
    'OH': 'OHIO',
    'OK': 'OKLAHOMA',
    'OR': 'OREGON',
    'PA': 'PENNSYLVANIA',
    'RI': 'RHODE ISLAND',
    'SC': 'SOUTH CAROLINA',
    'SD': 'SOUTH DAKOTA',
    'TN': 'TENNESSEE',
    'TX': 'TEXAS',
    'UT': 'UTAH',
    'VT': 'VERMONT',
    'VA': 'VIRGINIA',
    'WA': 'WASHINGTON',
    'WV': 'WEST VIRGINIA',
    'WI': 'WISCONSIN',
    'WY': 'WYOMING',
    'DC': 'DISTRICT OF COLUMBIA',
    'MP': 'NORTHERN MARIANA ISLANDS',
    'PW': 'PALAU',
    'PR': 'PUERTO RICO',
    'VI': 'VIRGIN ISLANDS'
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))


class ValidationConstants:
    UUID_REGEX = "[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}"
    DATE_REGEX = "^\d{4}(-|\/)((0[1-9])|(1[0-2]))(-|\/)((0[1-9])|([1-2][0-9])|(3[0-1]))$"
    SSN_REGEX = "^\d{9}$"
    POSTAL_CODE_REGEX = '^[0-9]{5}(?:-[0-9]{4})?$'
    UTC_DATE_TIME_REGEX = "^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\\.[0-9]+)?(Z)?$"
    EMAIL_REGEX = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}"


def validateStateField(state: str):
    if len(state) == 0:
        return None
    if state.upper() in abbrev_us_state:
        return abbrev_us_state[state.upper()]
    if state.upper() in us_state_abbrev:
        return state.upper()
    return None


def validatePostalCode(_code):
    if len(_code) == 0:
        return None
    regex_PostalCode = ValidationConstants.POSTAL_CODE_REGEX
    valid_Pattern = re.compile(regex_PostalCode)

    if valid_Pattern.match(_code) is not None:
        return _code
    else:
        return None


def validatePlatformResponse(_responseCode):
    _isValid = False
    _error = {}

    if _responseCode == 200:
        _isValid = True
    elif _responseCode == 404:
        _error[QuextIntegrationConstants.PLATFORM_DATA] = 'Invalid Platform Data'
    elif _responseCode == 400:
        _error[QuextIntegrationConstants.PLATFORM_DATA] = 'Invalid Platform Data'
    return _isValid, _error


def convertCountryToAplha3(country):
    if len(country) == 0:
        return None
    if country in pycountry.countries:
        return country.alpha_3
    if country == (pycountry.countries.get(alpha_3=country)).alpha_3:
        return country

    return None


def validateUUIDFormat(_uuid: str):
    regex_Date = ValidationConstants.UUID_REGEX
    valid_Pattern = re.compile(regex_Date)

    if valid_Pattern.match(_uuid) is not None:
        return True
    return False


def validatePlatformData(_data):
    responseObj = {QuextIntegrationConstants.DATA: {},
                   QuextIntegrationConstants.ERROR: {}}
    try:
        if validateUUIDFormat(_data.communityUUID) and validateUUIDFormat(
                _data.customerUUID):
            return True, {}
        else:
            if not validateUUIDFormat(_data.communityUUID):
                responseObj[QuextIntegrationConstants.ERROR][
                    QuextIntegrationConstants.COMMUNITY_UUID] = 'Invalid Community UUID'
            if not validateUUIDFormat(_data.customerUUID):
                responseObj[QuextIntegrationConstants.ERROR][
                    QuextIntegrationConstants.CUSTOMER_UUID] = 'Invalid Customer UUID'
            return False, responseObj
    except:
        if QuextIntegrationConstants.COMMUNITY_UUID not in _data:
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.COMMUNITY_UUID] = 'Missing Community UUID'
        if QuextIntegrationConstants.CUSTOMER_UUID not in _data:
            responseObj[QuextIntegrationConstants.ERROR][
                QuextIntegrationConstants.CUSTOMER_UUID] = 'Missing Customer UUID'
        return False, responseObj


def encrypt(raw, SECRET_KEY):
    """
    Encryption of the raw string using the custom created secret key
    """
    BS = 16
    key = hashlib.md5(SECRET_KEY.encode('utf8')).hexdigest()[:BS]
    def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    if isinstance(raw, bytes):
        raw = raw.decode('utf-8')
    raw = pad(raw).encode("UTF-8")
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(key.encode("UTF-8"), AES.MODE_CBC, iv)
    return base64.urlsafe_b64encode(iv + cipher.encrypt(raw)).decode('utf-8')


def decrypt(encryptedString, encrypted_key):
    key = base64.b64decode(encrypted_key)

    encryptedObj = json.loads(base64.b64decode(encryptedString).decode())

    IV = base64.b64decode(encryptedObj['iv'])
    encrypedValue = base64.b64decode(encryptedObj['value'])

    decobj = AES.new(key, AES.MODE_CBC, IV)
    data = decobj.decrypt(encrypedValue)
    return unpad(data, 16)

def date_validation(dates):
    date_obj = datetime.strptime(dates, '%Y-%m-%dT%H:%M:%S.%f')
    return date_obj

def date_filter(table_obj, query, servicerequest:ServiceRequest):
    try:
        if servicerequest.created_after:
            date_obj = date_validation(servicerequest.created_after)
            query = query.filter(table_obj.created_date > date_obj)
        if servicerequest.updated_after:
            date_obj = date_validation(servicerequest.updated_after)
            query = query.filter(table_obj.updated_date > date_obj)
        if servicerequest.created_before:
            date_obj = date_validation(servicerequest.created_before)
            query = query.filter(table_obj.created_date < date_obj)
        if servicerequest.updated_before:
            date_obj = date_validation(servicerequest.updated_before)
            query = query.filter(table_obj.updated_date < date_obj)
    except Exception as e:
        raise Exception(e)
    return query


class DataValidation:

    @staticmethod
    def formatError(obj, key, clipBoard, duplicateKey):
        """ Format the error dict into clipBoard"""
        if isinstance(obj, dict):
            return {k: DataValidation.formatError(v, k, clipBoard, duplicateKey) for k, v in obj.items()}
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], str):
            if key not in duplicateKey:
                if "regex" in obj[0] or "missing" in obj[0]:
                    clipBoard.update({key: 'invalid ' + key})
                    duplicateKey.append(key)
                    return obj[0]
                else:
                    clipBoard.update({key: obj[0]})
                    duplicateKey.append(key)
                    return obj[0]
        elif all(isinstance(key, int) for key in obj[0].keys()):
            clipBoard.update({key: 'invalid ' + key})
            return obj[0]
        elif isinstance(obj, list) and len(obj) == 1 and isinstance(obj[0], dict):
            return DataValidation.formatError(obj[0], None, clipBoard, duplicateKey)
        elif isinstance(obj, list) and len(obj) > 1:
            return {k: DataValidation.formatError(v, k, clipBoard, duplicateKey) for k, v in obj}

    @staticmethod
    def schema(_schemaType: Schema, _data):
        """ Validate the _data schema with _schemaType and return appropriate validation status and validation errors"""
        v = Validator()
        isValid = v.validate(_data, Validation_Schema[_schemaType])
        error = {}
        logging.info("validator error: {}".format(v.errors))
        DataValidation.formatError(v.errors, None, error, [])
        return isValid, Convert.toDict(error)

    @staticmethod
    def getPlatformRequestData(_data, _purpose: str):
        error = {}
        param = {}
        _isValid, _error = DataValidation.schema(Schema.PLATFORM_DATA, _data)
        if _isValid:
            param = {
                QuextIntegrationConstants.COMMUNITY_UUID: _data['communityUUID'],
                QuextIntegrationConstants.CUSTOMER_UUID: _data['customerUUID'],
                QuextIntegrationConstants.PURPOSE: _purpose
            }
        else:
            error = {QuextIntegrationConstants.RESPONSE_CODE: QuextIntegrationConstants.HTTP_BAD_RESPONSE_CODE,
                     QuextIntegrationConstants.RESPONSE_MESSAGE: _error}
        return param, error

    @staticmethod
    def validateCustomerUUID(_data):
        _isValid, _error = DataValidation.schema(Schema.CUSTOMER_UUID, _data)
        return _isValid, _error

class DataController:
    def getData(self, common_data: CommonStructure, callback_list: [object], dataSource: Datasource,
                params: dict = None):
        error = None
        for obj in callback_list:
            if error is None:
                common_data, error = obj(common_data, dataSource, params) 
                if not common_data:
                    return False, {}             
        return common_data, error

    def getResponseData(self, data: CommonStructure, callback):
        return callback(data)

    def executeOperation(self, common_data: CommonStructure, callback_list: [object]):
        error = None
        for obj in callback_list:
            if error is None:
                common_data, error = obj(common_data)
        return common_data, error


Validation_Schema = {
    Schema.NONE: None,
    Schema.PLATFORM_DATA: {
        'communityUUID': {'required': True,
                          'type': 'string',
                          'regex': ValidationConstants.UUID_REGEX},
        'customerUUID': {'required': True,
                         'type': 'string',
                         'regex': ValidationConstants.UUID_REGEX},
        'apiKey': {'required': True,
                   'type': 'string',
                   'regex': ValidationConstants.UUID_REGEX}
    },
    Schema.UNIT_AVAILABILITY: {
        'platformData': {
            'required': True,
            'type': 'dict',
            'schema': {
                'communityUUID': {'required': True,
                                  'type': 'list',
                                  'schema':
                                        {'type': 'string', 'regex': ValidationConstants.UUID_REGEX}
                                  },
                'customerUUID': { 'required': True,
                                   'type': 'string',
                                   'regex': ValidationConstants.UUID_REGEX}                                 
            }
        },
        'filter_on_availability': {'required': False,
                                   'type': 'boolean'},
        'available_start_date': {'required': False,
                                 'type': 'string',
                                 'regex': ValidationConstants.UTC_DATE_TIME_REGEX},
        'available_end_date': {'required': False,
                               'type': 'string',
                               'regex': ValidationConstants.UTC_DATE_TIME_REGEX}
    },
    Schema.TOUR_AVAILABILITY: {
        'platformData': {
            'required': True,
            'type': 'dict',
            'schema': {
                'communityUUID': {'required': True,
                                  'type': 'string',
                                  'regex': ValidationConstants.UUID_REGEX},
                'customerUUID': {'required': True,
                                 'type': 'string',
                                 'regex': ValidationConstants.UUID_REGEX}
            }
        },
        'timeData': {
            'required': True,
            'type': 'dict',
            'schema': {
                'fromDate': {'required': True,
                                  'type': 'string',
                                  'regex': ValidationConstants.UTC_DATE_TIME_REGEX},
                'toDate': {'required': True,
                                 'type': 'string',
                                 'regex': ValidationConstants.UTC_DATE_TIME_REGEX}
            }
        }
    },
    Schema.CUSTOMER_UUID: {
        'customerUUID': {'required': True,
                         'type': 'string',
                         'regex': ValidationConstants.UUID_REGEX}
    },
    Schema.COMMUNITY: {
        'community_id': {
            'required': True,
            'type': 'integer'
        }
    },
    Schema.RESIDENTS: {
        'move_in_date': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.DATE_REGEX
        },
        'move_out_date': {
            'required': True,
            'empty': True,
            'regex': ValidationConstants.DATE_REGEX
        }
    },
    Schema.PROSPECTS: {
        'create_date': {
            'required': True,
            'regex': ValidationConstants.DATE_REGEX
        }
    },
    Schema.TRANSACTIONS: {
        'resident_id': {
            'required': True,
            'type': 'integer'
        },
        'start_date': {
            'required': True,
            'regex': ValidationConstants.DATE_REGEX
        },
        'end_date': {
            'required': True,
            'regex': ValidationConstants.DATE_REGEX
        }
    },
    Schema.CUSTOMER_EVENTS: {
        'start_date': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.DATE_REGEX
        },
        'end_date': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.DATE_REGEX
        }
    },
    Schema.UNIT_AVAILABLE_PRICE_PAYLOAD: {
        'FloorLevel': {
            'required': True,
            'type': 'integer',
            'minlength': 1
        },
        'UnitBathrooms': {
            'required': True,
            'type': 'number',
            'minlength': 1
        },
        'UnitBedrooms': {
            'required': True,
            'type': 'integer',
            'minlength': 1
        },
        'includeConcessionsInLeaseTermPricing': {
            'required': False,
            'type': 'boolean',
            'minlength': 1
        }
    },
    Schema.REAL_PAGE_GUESTCARD_PAYLOAD: {
        'firstname': {'required': True,
                          'type': 'string'},
        'lastname': {'required': True,
                         'type': 'string'},
        'phonenumber': {'required': False,
                         'type': 'string'},
        'email': {'required': False,
                         'type': 'string'},
        'relationshipid': {'required': False,
                         'type': 'string'}
    },
    Schema.GUEST_CARDS: {
        'platformData': {
            'required': True,
            'type': 'dict',
            'schema': {
                'communityUUID': {'required': True,
                                  'type': 'string',
                                  'regex': ValidationConstants.UUID_REGEX},
                'customerUUID': {'required': True,
                                 'type': 'string',
                                 'regex': ValidationConstants.UUID_REGEX}
            }
        },
        'guest': {
            'type': 'dict',
            'schema': {
                'first_name': {
                    'required': True,
                    'type': 'string',
                    'nullable': False,
                    'empty': False
                },
                'last_name': {
                    'required': True,
                    'type': 'string',
                    'nullable': False,
                    'empty': False
                },
                'phone': {
                    'required': False,
                    'type': 'string',
                    'minlength': 10,
                    'maxlength': 10,
                    'nullable': True,
                    'empty': False
                },
                'email': {
                    'required': True,
                    'type': 'string',
                    'nullable': False,
                    'empty': False,
                    'regex': ValidationConstants.EMAIL_REGEX
                },
                'phone_country_code':{
                    'required': False,
                    'type': 'string',
                    'nullable': True,
                    'empty': False
                }
            }
        },
        'guestComment': {
            'required': False,
            'type': 'string',
            'nullable': True
        },
        'tourScheduleData': {
            'type': 'dict',
            'required': False,
            'schema': {
                'start': {
                    'required': True,
                    'type': 'string',
                    'nullable': False,
                    'empty': False,
                    'regex': ValidationConstants.UTC_DATE_TIME_REGEX
                }
            }
        },
        'guestPreference': {
            'type': 'dict',
            'schema': {
                'desiredBeds': {
                    'required': False,
                    'type': 'list',
                    'nullable':True,
                    'schema': {'type': 'string'}
                },
                'desiredRent': {
                    'required': False,
                    'type': 'integer',
                    'nullable': True
                },
                'desiredBaths': {
                    'required': False,
                    'type': 'list',
                    'nullable': True,
                    'schema': {'type': 'integer'}
                },
                'moveInDate': {
                    'required': False,
                    'type': 'string',
                    'regex': ValidationConstants.DATE_REGEX,
                    'nullable': True
                },
                'contactPreference': {
                    'required': False,
                    'type': 'list',
                    'nullable': True
                },
                'leaseTermMonths': {
                    'required': False,
                    'type': 'integer',
                    'nullable': True
                },
                'noOfOccupants': {
                    'required': False,
                    'type': 'integer',
                    'nullable': True
                },
                'moveInReason': {
                    'required': False,
                    'type': 'string',
                    'nullable': True
                },
                'preferredAmenities': {
                    'required': False,
                    'type': 'string',
                    'nullable': True
                }
            }
        }
    },
    Schema.REAL_PAGE_GET_AGENT_APPOINTMENT_TIME: {
        'getagentsappointmenttimes': {
            'type': 'dict', 
            'schema': {
                'leasingagent': {
                    'type': 'list', 
                    'required': True, 
                    'minlength': 1}
                    },
            'required':True}
    },
    Schema.TOUR_SCHEDULE_PAYLOAD: {
        'appointmentData': {
            'type': 'dict',
            'schema':{
                'firstName': {
                    'required': True,
                    'type': 'string'},
                'lastName': {
                    'required': True,
                    'type': 'string'},
                'phone': {
                    'required': False,
                    'type': 'string',
                    'minlength': 10,
                    'maxlength': 10},
                'email': {
                    'required': True,
                    'type': 'string'}
                },
            'required':True}
    },
    Schema.ENTRATA_GUESTCARD_PAYLOAD: {
        'firstName': {
            'required': True,
            'type': 'string'
        },
        'lastName': {
            'required': True,
            'type': 'string'
        },
        'personalPhoneNumber': {
            'required': True,
            'type': 'string',
            'minlength': 10,
            'maxlength': 10
        },
        'email': {
            'required': True,
            'type': 'string'
        },
        'eventdate': {
            'required': True,
            'type': 'string',
            'regex': ValidationConstants.DATE_REGEX
        },
        'eventReason': {
            'required': True,
            'type': 'string'
        }
    }
}

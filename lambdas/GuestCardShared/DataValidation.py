import re
from datetime import date


class BasePlatformData:
    communityUUID: str
    customerUUID: str


class BaseGuestCardData:
    propertyName: str
    firstName: str
    lastName: str
    phone: str
    email: str
    notes: str


response_header = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, HEAD, OPTIONS'
}


class DataValidation:
    @staticmethod
    def validatePlatformRequestData(data: BasePlatformData, purpose: str):
        error = {}
        param = {}
        _isValid, _error = DataValidation.validatePlatformData(data)
        if _isValid:
            param = {
                GuestCardIntegrationConstant.COMMUNITY_UUID: data.communityUUID,
                GuestCardIntegrationConstant.CUSTOMER_UUID: data.customerUUID,
                GuestCardIntegrationConstant.PURPOSE: purpose
            }
        else:
            error = {GuestCardIntegrationConstant.RESPONSE_CODE: 400,
                     GuestCardIntegrationConstant.RESPONSE_MESSAGE: _error}
        return param, error

    @staticmethod
    def validatePlatformData(data: BasePlatformData):
        error = {GuestCardIntegrationConstant.SUCCESS: {}, GuestCardIntegrationConstant.DATA: {},
                 GuestCardIntegrationConstant.ERROR: {}}
        try:
            if DataValidation.isvalidUUIDFormat(data.communityUUID) and \
                    DataValidation.isvalidUUIDFormat(data.customerUUID):
                return True, error
            else:
                if not DataValidation.isvalidUUIDFormat(data.communityUUID):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.COMMUNITY_UUID] = \
                        'Invalid Community UUID'
                if not DataValidation.isvalidUUIDFormat(data.customerUUID):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.CUSTOMER_UUID] = \
                        'Invalid Customer UUID'
                error[GuestCardIntegrationConstant.SUCCESS] = False
                return False, error
        except:
            if GuestCardIntegrationConstant.COMMUNITY_UUID not in data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.COMMUNITY_UUID] = \
                    'Missing Community UUID'
            if GuestCardIntegrationConstant.CUSTOMER_UUID not in data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.CUSTOMER_UUID] = \
                    'Missing Customer UUID'
            error[GuestCardIntegrationConstant.SUCCESS] = False
            return False, error

    @staticmethod
    def isvalidUUIDFormat(_uuid: str):
        regex_Date = '[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
        valid_Pattern = re.compile(regex_Date)

        if valid_Pattern.match(_uuid) is not None:
            return True
        return False

    @staticmethod
    def validatePlatformResponse(response_Code):
        _isValid = False
        _error = {}

        if response_Code == 200:
            _isValid = True
        elif response_Code == 404:
            _error[GuestCardIntegrationConstant.PLATFORM_DATA] = 'Invalid Platform Data'
        elif response_Code == 400:
            _error[GuestCardIntegrationConstant.PLATFORM_DATA] = 'Invalid Platform Data'
        return _isValid, _error

    @staticmethod
    def validateEmailAddress(_email: str):
        regex_Email = '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
        valid_Pattern = re.compile(regex_Email)

        if valid_Pattern.match(_email) is not None:
            return True
        return False

    @staticmethod
    def validatePhoneNumber(_phone: str):
        regex_Phone = '^(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?$'
        valid_Pattern = re.compile(regex_Phone)

        if valid_Pattern.match(_phone) is not None:
            return True
        else:
            return False

    @staticmethod
    def validatePostalCode(_code):
        regex_PostalCode = '^[0-9]{5}(?:-[0-9]{4})?$'
        valid_Pattern = re.compile(regex_PostalCode)

        if valid_Pattern.match(_code) is not None:
            return True
        else:
            return False

    @staticmethod
    def validateStringField(_field):
        if type(_field) is str and (len(_field) > 0):
            return True
        return False

    @staticmethod
    def validateBaseGuestCardFormData(_data: BaseGuestCardData):
        error = {GuestCardIntegrationConstant.SUCCESS: {}, GuestCardIntegrationConstant.DATA: {},
                 GuestCardIntegrationConstant.ERROR: {}}
        try:
            if DataValidation.validateStringField(_data.firstName) and \
                    DataValidation.validateStringField(_data.lastName) and \
                    DataValidation.validateStringField(_data.propertyName) and \
                    DataValidation.validateStringField(_data.notes):
                if (GuestCardIntegrationConstant.EMAIL in _data and DataValidation.validateEmailAddress(
                        _data.email)) or (GuestCardIntegrationConstant.PHONE in _data and
                                          DataValidation.validatePhoneNumber(_data.phone)):
                    return True, error
                else:
                    if GuestCardIntegrationConstant.EMAIL not in _data:
                        error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.EMAIL] = 'Missing Email'
                    else:
                        error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.EMAIL] = 'Invalid Email'
                    if GuestCardIntegrationConstant.PHONE not in _data:
                        error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PHONE] = 'Missing Phone'
                    else:
                        error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PHONE] = 'Invalid Phone Number'
                    error[GuestCardIntegrationConstant.SUCCESS] = False
                    return False, error
            else:
                if not DataValidation.validateStringField(_data.firstName):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.FIRST_NAME] = 'Invalid First Name'
                if not DataValidation.validateStringField(_data.lastName):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.LAST_NAME] = 'Invalid Last Name'
                if not DataValidation.validateStringField(_data.propertyName):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PROPERTY_NAME] = 'Invalid Property Name'
                if not DataValidation.validateEmailAddress(_data.email):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.EMAIL] = 'Invalid Email'
                if not DataValidation.validatePhoneNumber(_data.phone):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PHONE] = 'Invalid Phone Number'
                if not DataValidation.validatePhoneNumber(_data.notes):
                    error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.NOTES] = 'Invalid Notes'
                error[GuestCardIntegrationConstant.SUCCESS] = False
                return False, error
        except:
            if GuestCardIntegrationConstant.FIRST_NAME not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.FIRST_NAME] = 'Missing First Name'
            if GuestCardIntegrationConstant.LAST_NAME not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.LAST_NAME] = 'Missing Last Name'
            if GuestCardIntegrationConstant.PROPERTY_NAME not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PROPERTY_NAME] = 'Missing Property Name'
            if GuestCardIntegrationConstant.EMAIL not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.EMAIL] = 'Missing Email'
            if GuestCardIntegrationConstant.PHONE not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.PHONE] = 'Missing Phone'
            if GuestCardIntegrationConstant.NOTES not in _data:
                error[GuestCardIntegrationConstant.ERROR][GuestCardIntegrationConstant.NOTES] = 'Missing Notes'
            error[GuestCardIntegrationConstant.SUCCESS] = False
            return False, error


def serialize_object(obj):
    if isinstance(obj, date):
        serial = obj.isoformat()
        return serial
    return obj.__dict__


class GuestCardIntegrationConstant:
    COMMUNITY_UUID = 'communityUUID'
    PLATFORM_OUTGOING_CHANNEL = 'Platform_Outgoing_Channel'
    CUSTOMER_UUID = 'customerUUID'
    RESPONSE_CODE = 'responseCode'
    RESPONSE_MESSAGE = 'responseMessage'
    SUCCESS = 'success'
    ERRORS = 'errors'
    DATA = 'data'
    SUCCESS_MESSAGE = 'GuestCard submitted successfully'
    ERROR = 'error'
    HTTP_BAD_RESPONSE_CODE = 400
    HTTP_GOOD_RESPONSE_CODE = 200
    PURPOSE = 'purpose'
    SEND_GUEST_CARD = 'createGuestcard'
    PLATFORM_DATA = 'platformData'
    SEND_GUEST_CARD_METHOD = 'getOutgoingChannelData'
    FORMAT_GUEST_CARD_DATA_METHOD = 'formatOutgoingChannelResponse'
    FIRST_NAME = 'firstName'
    LAST_NAME = 'lastName'
    EMAIL = 'email'
    PHONE = 'phone'
    PROPERTY_NAME = 'propertyName'
    NOTES = 'notes'

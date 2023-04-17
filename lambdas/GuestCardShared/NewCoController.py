from GuestCardShared.DataValidation import BasePlatformData, BaseGuestCardData, DataValidation, \
    GuestCardIntegrationConstant, serialize_object
from GuestCardShared.Interface import Interface


class NewCoPayload:
    property: str
    first_name: str
    last_name: str
    email: str
    phone: str
    notes: str
    postal_code: str
    pets: str
    city: str
    state: str
    unit_number: str

    def __init__(self, property: str, first_name: str, last_name: str, email: str, phone: str, notes: str,
                 postal_code: str, pets: str,
                 city: str, state: str, unit_number: str) -> None:
        self.property = property
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.notes = notes
        self.postal_code = postal_code
        self.pets = pets
        self.city = city
        self.state = state
        self.unit_number = unit_number


class NewCoPlatformData:
    def __init__(self, platformID: str) -> None:
        self.platformID = platformID


def convertPlatformData(_data: dict):
    platForm_Data = NewCoPlatformData(_data['providerID'])
    return platForm_Data


def validateNewCoGuestCardData(data: BaseGuestCardData):
    error = {}
    isValid, error = DataValidation.validateBaseGuestCardFormData(data)
    # add other validations for the GuestCardData
    if isValid:
        return True, error, GuestCardIntegrationConstant.HTTP_GOOD_RESPONSE_CODE
    return False, error, GuestCardIntegrationConstant.HTTP_BAD_RESPONSE_CODE


def validateNewCoPlatformData(_data: NewCoPlatformData):
    error = {}
    if DataValidation.validateStringField(
            _data.platformID):
        return True, error, GuestCardIntegrationConstant.HTTP_GOOD_RESPONSE_CODE
    else:
        error['platformData'] = 'Invalid Platform Data'
        return False, error, GuestCardIntegrationConstant.HTTP_BAD_RESPONSE_CODE


class NewCoController(Interface):
    def getOutgoingChannelData(self, guestCard_data: BaseGuestCardData, platform_data: dict):
        # creating Periodic tour_scheduling API body.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}
        # platform_Data = convertPlatformData(platform_data)

        # _isValidPlatformData, _errorPlatformDataResponse, _errorPlatformDataResponseCode = validateNewCoPlatformData(
        #     platform_Data)

        _isValidGuestCardData, _errorGuestCardDataResponse, _errorGuestCardDataResponseCode = validateNewCoGuestCardData(
            guestCard_data)

        if _isValidGuestCardData:
            email = '' if (GuestCardIntegrationConstant.EMAIL not in guestCard_data) else guestCard_data.email
            phone = '' if (GuestCardIntegrationConstant.PHONE not in guestCard_data) else guestCard_data.phone
            body = serialize_object(
                NewCoPayload(guestCard_data.propertyName, guestCard_data.firstName, guestCard_data.lastName,
                             email, phone, guestCard_data.notes, "", "",
                             "", "", ""))
            self.Body = body
        else:
            if not _isValidGuestCardData:
                self.Error = {GuestCardIntegrationConstant.RESPONSE_CODE: _errorGuestCardDataResponseCode,
                              GuestCardIntegrationConstant.RESPONSE_MESSAGE: _errorGuestCardDataResponse}

        # returning nestio tour_scheduling API body, headers & parameters
        return self.Body, self.Headers, self.Params, self.Error

    def formatOutgoingChannelResponse(self, _data: dict):
        response = {GuestCardIntegrationConstant.SUCCESS: {}, GuestCardIntegrationConstant.DATA: {},
                    GuestCardIntegrationConstant.ERROR: {}}
        response_Code = _data[GuestCardIntegrationConstant.RESPONSE_CODE]
        if response_Code == 200:
            if GuestCardIntegrationConstant.SUCCESS not in _data[GuestCardIntegrationConstant.RESPONSE_MESSAGE]:
                response[GuestCardIntegrationConstant.DATA] = GuestCardIntegrationConstant.SUCCESS_MESSAGE
                response[GuestCardIntegrationConstant.SUCCESS] = True
            else:
                response_Code = 400
                response[GuestCardIntegrationConstant.SUCCESS] = False
                response[GuestCardIntegrationConstant.ERROR] = \
                    _data[GuestCardIntegrationConstant.RESPONSE_MESSAGE][GuestCardIntegrationConstant.ERRORS]
        else:
            response_Code = 400
            response[GuestCardIntegrationConstant.SUCCESS] = False
            response[GuestCardIntegrationConstant.ERROR] = _data[GuestCardIntegrationConstant.RESPONSE_MESSAGE]
        return response, response_Code

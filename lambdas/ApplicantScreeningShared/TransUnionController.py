import base64
import binascii
import hashlib
import hmac
import random
import re
from collections import defaultdict
import os
import dicttoxml as dicttoxml


from ApplicantScreeningShared.DataValidation import BaseApplicationScreeningData, BaseApplicantScreeningResponse, \
    ScreeningErrorType, BaseErrorItem, DataValidation, BaseApplicant, ApplicantScreeningConstants, usStateAbbrev, \
    BaseApplicationRetrievalData
from ApplicantScreeningShared.IntegrationInterface import IntegrationInterface
from typing import List
from TransUnionShared.Config import config

class Agent:
    memberName: str
    password: str
    propertyId: str
    sourceId: str
    responseURL: str

    def __init__(self, member_name, password, property_id, source_id, response_url):
        self.memberName = member_name
        self.password = password
        self.propertyId = property_id
        self.sourceId = source_id
        self.responseURL = response_url


class ScreeningType:
    criminal: str
    eviction: str
    credit: str

    def __init__(self, criminal, eviction, credit):
        self.criminal = criminal
        self.eviction = eviction
        self.credit = credit


class Applicant:
    sourceRef: str
    applicantType: str
    firstName: str
    middleName: str
    lastName: str
    nameSuffix: str
    dateOfBirth: str
    email: str
    streetAddress: str
    city: str
    state: str
    postalCode: str
    ssn: str
    employmentIncome: str
    employmentIncomePeriod: str
    otherIncome: str
    otherIncomePeriod: str
    assets: str
    employmentStatus: str
    screeningType: ScreeningType

    def __init__(self, source_ref, applicant_type, first_name, middle_name, last_name,
                 name_suffix, date_of_birth, email, street_address, city, state,
                 postal_code, ssn, employment_income, employment_income_period, other_income,
                 other_income_period, assets, employment_status, screening_type):
        self.sourceRef = source_ref
        self.applicantType = applicant_type
        self.firstName = first_name
        self.middleName = middle_name
        self.lastName = last_name
        self.nameSuffix = name_suffix
        self.dateOfBirth = date_of_birth
        self.email = email
        self.streetAddress = street_address
        self.city = city
        self.state = state
        self.postalCode = postal_code
        self.ssn = ssn
        self.employmentIncome = employment_income
        self.employmentIncomePeriod = employment_income_period
        self.otherIncome = other_income
        self.otherIncomePeriod = other_income_period
        self.assets = assets
        self.employmentStatus = employment_status
        self.screeningType = screening_type


class Application:
    sourceRef: str
    rentAmount: str
    depositAmount: str
    leaseTerm: str
    guestCard: str
    photoIdVerified: str
    applicants: List[Applicant]

    def __init__(self, source_ref, rent_amount, deposit_amount, lease_term, guest_card, photo_id_verified, applicants):
        self.sourceRef = source_ref
        self.rentAmount = rent_amount
        self.depositAmount = deposit_amount
        self.leaseTerm = lease_term
        self.guestCard = guest_card
        self.photoIdVerified = photo_id_verified
        self.applicants = applicants


class Gateway:
    version: str
    agent: Agent
    application: Application

    def __init__(self, version, agent, application):
        self.version = version
        self.agent = agent
        self.application = application


class CreateApplicationPayload:
    gateway: Gateway

    def __init__(self, gateway):
        self.gateway = gateway


class RetrievalApplication:
    applicationNumber: str
    sourceRef: str

    def __init__(self, applicationNumber='', sourceRef=''):
        self.applicationNumber = applicationNumber
        self.sourceRef = sourceRef


class RetrievalGateway:
    version: str
    agent: Agent
    application: RetrievalApplication

    def __init__(self, version, agent, application):
        self.version = version
        self.agent = agent
        self.application = application


class RetrieveApplicationPayload:
    gateway: RetrievalGateway

    def __init__(self, gateway):
        self.gateway = gateway


def createApplicantSourceRef(_data: BaseApplicant):
    applicantSourceRef = str(_data.address.streetAddress[-1:]) + str(_data.firstName[:2]) + \
                         str(_data.lastName[-2:]) + str(_data.birthDate) + \
                         str(usStateAbbrev[_data.address.state.upper()]) + str(random.randrange(1, 1000))
    return applicantSourceRef


def createApplicationSourceRef(_data: List[BaseApplicant]):
    applicationSourceRef = ''
    for item in _data:
        applicantSourceRef = createApplicantSourceRef(item)
        applicationSourceRef += applicantSourceRef
    return applicationSourceRef


def validateApplicantData(_data: List[BaseApplicant]):
    error = {}
    isValid = True
    for item in _data:
        if len(item.firstName) < 2 and \
                ('firstName' not in error):
            isValid = False
            error['firstName'] = 'First Name should be at least two characters'
        if len(item.lastName) < 2 and \
                ('lastName' not in error):
            isValid = False
            error['lastName'] = 'Last Name should be at least two characters'
        if int(item.employmentStatus) not in range(1, 5) and \
                ('employmentStatus' not in error):
            isValid = False
            error['employmentStatus'] = 'Employment status must be 1 to 4'
        if not (item.employmentIncome.isdigit() and
                ((int(item.employmentStatus) == 1 and int(item.employmentIncome) > 0) or
                 (int(item.employmentStatus) != 1 and int(item.employmentIncome) >= 0))) and \
                ('incomeAmount' not in error):
            isValid = False
            error['incomeAmount'] = 'Income Amount must me greater than or equal to 0'
        if int(item.employmentIncomePeriod) in range(1, 4) and \
                ('incomePeriod' not in error):
            isValid = False
            error['incomePeriod'] = 'Employment Income Period must be 1 to 3'
        if len(item.assetsValue) != 0:
            if not (int(item.assetsValue) < 0) and ('assets' not in error):
                isValid = False
                error['assets'] = 'Assets value must greater than or equal to 0'
    if isValid:
        return True, {}
    return False, error


def validateAmountField(_amount: str, lower: int, higher: int):
    if len(_amount) != 0:
        return _amount.isdigit() and lower <= int(_amount) <= higher
    return True


def validateRetrieveApplicationRequestData(_applicationData: BaseApplicationRetrievalData, _platformData):
    responseObj = BaseApplicantScreeningResponse()
    if (ApplicantScreeningConstants.APPLICATION_NUMBER in _applicationData) or (
            ApplicantScreeningConstants.REFERENCE_ID in _applicationData):
        return True, {}
    else:
        responseObj.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
        responseObj.error.ErrorMessage = 'Either Application Number or ReferenceId must be specified'
        return False, DataValidation.createApplicationScreeningResponse(responseObj, responseObj.data,
                                                                        responseObj.data.applicants,
                                                                        responseObj.data.screeningResult,
                                                                        responseObj.error)


def validateCreateApplicationRequestData(_applicationData, _platformData):
    responseObj = BaseApplicantScreeningResponse()
    if 'depositAmount' not in _applicationData:
        _applicationData['depositAmount'] = '0'
    if (validateAmountField(_applicationData.rentAmount, 0, 25000) and
            validateAmountField(_applicationData.depositAmount, 0, 50000) and
            1 <= int(_applicationData.leaseTerm) <= 999 and int(_applicationData.marketingSource) in range(1, 39) and
            len(_applicationData.applicants) > 0 and validateApplicantData(_applicationData.applicants)):
        return True, {}
    else:
        responseObj.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
        if not (_applicationData.rentAmount.isdigit()):
            _errorItem = BaseErrorItem('rentAmount', 'Rent amount must be full dollar amounts only')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if not (0 <= int(_applicationData.rentAmount) <= 25000):
            _errorItem = BaseErrorItem('rentAmount', 'Rent value must be 0<= n <= 25000')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if not (_applicationData.depositAmount.isdigit()) and len(_applicationData.depositAmount) != 0:
            _errorItem = BaseErrorItem('depositAmount',
                                       'Deposit amount must be full dollar amounts only')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_applicationData.depositAmount) != 0:
            if not (0 <= int(_applicationData.depositAmount) <= 50000):
                _errorItem = BaseErrorItem('depositAmount', 'Deposit value must be 0<= n <= 50000')
                responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))

        if not (1 <= int(_applicationData.leaseTerm) > 999):
            _errorItem = BaseErrorItem('leaseTerm', 'Lease Term value must be between 1 and 999')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if not (int(_applicationData.marketingSource) in range(1, 39)):
            _errorItem = BaseErrorItem('marketingSource', 'The Marketing source value must be '
                                                          'between 1 to 38')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))

        return False, DataValidation.createApplicationScreeningResponse(responseObj, responseObj.data,
                                                                        responseObj.data.applicants,
                                                                        responseObj.data.screeningResult,
                                                                        responseObj.error)


def createApplicantDataItem(_data: dict):
    applicant_dict = {'referenceId': _data['sourceRef'],
                      'firstName': _data['firstName'],
                      'middleName': _data['middleName'],
                      'lastName': _data['lastName'],
                      'streetAddress': _data['streetAddress'],
                      'city': _data['city'], 'state': _data['state'],
                      'postalCode': _data['postalCode']}

    return applicant_dict


def addMissingKeys(_data):
    optional_keys = ['middleName', 'suffix', 'otherIncome', "otherIncome", "otherIncomePeriod", "assetsValue", 'email']
    for key in optional_keys:
        if key not in _data:
            _data[key] = ' '


def cleanXMLTransUnionReport(response):
    return re.sub(r'(?s)(<BackgroundReport>)(.*?)(</BackgroundReport>)', '', response.text)


def structureObjectReportTransUnion(request):
    newRequest = {"gateway": request}
    newRequest['gateway']['version'] = 2
    newRequest['gateway']['agent'] = {
        "memberName": config["member_name"],
        "password": config["password"],
        "propertyId": config["property_id"],
        "sourceId": config["source_id"],
        "responseURL": config["trans_union_postback_url"]
    }
    return newRequest


class TransUnionConstants:
    PLATFORM_DATA = 'platformData'
    APPLICANT = 'applicant'
    VERSION = 'version'
    MEMBER_NAME = 'memberName'
    PASSWORD = 'password'
    PROPERTY_ID = 'screeningPropertyId'
    SOURCE_ID = 'sourceId'
    STATUS = 'status'
    STATUS_CODE = 'statusCode'
    GATEWAY = 'gateway'
    APPLICATION = 'application'
    APPLICANTS = 'applicants'
    APPLICANT_TYPE = '1'
    PHOTO_ID_VERIFIED = '1'
    POST_BACK_URL = 'https://integration-dev.quext.io:11223/api/trans-union-post-back'
    PROPERTY_ID_CODE = "1000002154"
    SECRET_KEY = os.environ['TRANS_UNION_SECRET_KEY']
    RESIDENT_ID = "tu-residentid "
    TRANSUNION_POST_BACK_URL = "https://zato.dev.quext.io/api/v1/screening/post-back"


def signature(key, msg):
    key = binascii.unhexlify(key)
    msg = msg.encode()
    return hmac.new(key, msg, hashlib.sha256)


def AuthEncryption(request, nonce, timestamp):
    propertyId = TransUnionConstants.PROPERTY_ID_CODE
    secretKey = TransUnionConstants.SECRET_KEY
    m5Request = hashlib.md5(request.encode())
    m5Request = base64.b64encode(m5Request.digest()).decode("utf-8")
    encodeMessage = propertyId + timestamp + nonce + m5Request
    base64Message = base64.b64encode(signature(secretKey.encode("utf-8").hex(), encodeMessage).digest())
    return base64Message.decode()


def replaceBodyContentTransUnion(response):
    words = {"TransactionStatus": "VerificationStatus", "RiskIndicator": "PotentialRisk"}
    for k in words:
        response = response.replace(k, words[k])
    return response


def isVerify(body):
    if "Answers" in body:
        return False
    elif "Applicant" in body:
        return True
    else:
        return False


class TransUnionController(IntegrationInterface):

    def getApplicantScreeningRequestData(self, _applicationData: BaseApplicationScreeningData, _platformData: dict):
        """
                @desc: this method will check for the _applicationData and returns the body, headers, params
                to verify resident details and the error.
                @param: _applicationData which contains the application information like rentAmount, lease term,
                marketing source, and applicant information like first name, last name, employment status,
                and so on, _platformData specific information like token, property ID and secret key.
                @return:the body, headers, params for the resident screening create application API and the error.
        """
        # creating TransUnionShared Resident Screening Create application API body and header.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}

        _valid, _error = validateCreateApplicationRequestData(_applicationData, _platformData)
        if _valid:
            serializeApplicantList = []
            for item in _applicationData.applicants:
                # calling a method to substitute default values for the missing keys
                addMissingKeys(item)
                serializeApplicantList.append(DataValidation.serialize_object(
                    Applicant(createApplicantSourceRef(item), TransUnionConstants.APPLICANT_TYPE, item.firstName,
                              item.middleName, item.lastName, item.suffix, item.birthDate, item.email,
                              item.address.streetAddress, item.address.city, usStateAbbrev[
                                  item.address.state.upper()],
                              item.address.postalCode, item.ssn, item.employmentIncome,
                              item.employmentIncomePeriod, item.otherIncome, item.otherIncomePeriod,
                              item.assetsValue, item.employmentStatus,
                              DataValidation.serialize_object(ScreeningType(item.criminal, item.eviction,
                                                                            item.credit)))))
            if "depositAmount" not in _applicationData:
                _applicationData.depositAmount = ' '
            self.Body = DataValidation.serialize_object(
                CreateApplicationPayload(DataValidation.serialize_object
                                         (Gateway(_platformData[TransUnionConstants.VERSION],
                                                  DataValidation.serialize_object(
                                                      Agent(_platformData[TransUnionConstants.MEMBER_NAME],
                                                            _platformData[TransUnionConstants.PASSWORD],
                                                            _platformData[TransUnionConstants.PROPERTY_ID],
                                                            _platformData[TransUnionConstants.SOURCE_ID],
                                                            TransUnionConstants.POST_BACK_URL)),
                                                  DataValidation.serialize_object(Application(
                                                      createApplicationSourceRef(_applicationData.applicants),
                                                      _applicationData.rentAmount, _applicationData.depositAmount,
                                                      _applicationData.leaseTerm,
                                                      _applicationData.marketingSource,
                                                      TransUnionConstants.PHOTO_ID_VERIFIED,
                                                      serializeApplicantList))))))

            self.Headers = {'Content-Type': 'text/xml; charset=UTF8',
                            'Accept': 'application/json'}
        else:
            self.Error = {
                ApplicantScreeningConstants.RESPONSE_CODE: ApplicantScreeningConstants.HTTP_BAD_RESPONSE_CODE,
                ApplicantScreeningConstants.RESPONSE_MESSAGE: _error}

        # returning Transunion Resident Screening Create Application API body, headers and parameters
        return dicttoxml.dicttoxml(self.Body, item_func=lambda x: x[:-1], attr_type=False, root=False).decode('utf-8'), \
               self.Headers, self.Params, self.Error

    def formatCreateApplicationResponse(self, _data: dict, _platformData: dict = None):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from Trans-Union regarding resident screening.
            @return: the formatted response and the http response status code.
        """
        responseBody = BaseApplicantScreeningResponse()
        responseCode = _data[ApplicantScreeningConstants.RESPONSE_CODE]
        statusCode = \
            int(_data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS][
                    TransUnionConstants.STATUS_CODE])
        if statusCode == 1 or statusCode == 15:
            responseBody.error.__delattr__('ErrorType')
            responseBody.error.__delattr__('ErrorMessage')
            responseBody.error.__delattr__('InvalidParameter')
            responseBody.data.referenceId = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['sourceRef']
            responseBody.data.applicationNumber = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['applicationNumber']
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
            if isinstance(_data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                              TransUnionConstants.APPLICATION][TransUnionConstants.APPLICANTS][
                              TransUnionConstants.APPLICANT], dict):
                responseBody.data.applicants.applicant = createApplicantDataItem(
                    _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                        TransUnionConstants.APPLICATION][TransUnionConstants.APPLICANTS][TransUnionConstants.APPLICANT])
            else:
                applicant_list = []
                for item in _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION][TransUnionConstants.APPLICANTS][TransUnionConstants.APPLICANT]:
                    applicant_list.append(createApplicantDataItem(item))
                responseBody.data.applicants.applicant = applicant_list
            responseBody.data.screeningResult.applicationStatus = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['scoreResult'][
                    'applicationRecommendationMessage']
            responseBody.data.screeningResult.criminalStatus = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['scoreResult'][
                    'criminalRecommendationMessage']
            responseBody.data.screeningResult.evictionStatus = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['scoreResult'][
                    'evictionRecommendationMessage']
            responseBody.data.screeningResult.creditStatus = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.APPLICATION]['scoreResult'][
                    'recommendationMessage']
            responseBody.data.screeningReport = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    'BackgroundReport']
        elif statusCode == 2:
            responseBody.error.ErrorType = ScreeningErrorType.SYSTEM_ERROR.value
            responseBody.error.ErrorMessage = 'System Error'
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 3:
            responseBody.error.ErrorType = ScreeningErrorType.SYSTEM_ERROR.value
            responseBody.error.ErrorMessage = 'System is temporarily unavailable'
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 4:
            responseBody.error.ErrorMessage = 'The request is not a well formed XML'
            responseBody.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 5:
            responseBody.error.ErrorMessage = 'The request body is missing a required field/ required field should ' \
                                              'not be empty '
            responseBody.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 6:
            responseBody.error.ErrorMessage = 'Member Name and/or Password are invalid'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 7:
            responseBody.error.ErrorMessage = 'Property Id is required for this member'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 8:
            responseBody.error.ErrorMessage = 'More than one property is associated with this member and no property ' \
                                              'id was supplied '
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 9:
            responseBody.error.ErrorMessage = 'Property id is Invalid'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 10:
            responseBody.error.ErrorMessage = 'Source Id is invalid'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 11:
            responseBody.error.ErrorMessage = 'IP address is not present in the access list for this source'
            responseBody.error.ErrorType = ScreeningErrorType.VALIDATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 12:
            responseBody.error.ErrorMessage = 'The property is not enabled with the appropriate checks'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 13:
            responseBody.error.ErrorMessage = 'This member is not enabled with the appropriate checks'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 14:
            responseBody.error.ErrorMessage = 'The application number specified is not found'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']

        elif statusCode == 16:
            responseBody.error.ErrorMessage = 'Transaction Timed out waiting for the response from the credit server'
            responseBody.error.ErrorType = ScreeningErrorType.SYSTEM_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 17:
            responseBody.error.ErrorMessage = 'The transaction id specified is not found'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 18:
            responseBody.error.ErrorMessage = 'Member must initially log on to https://ResidenScreenig.transunion.com in ' \
                                              'order to receive important Fair Credit Reporting act compliance materials ' \
                                              'before requests can be performed using this member name '
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        elif statusCode == 19:
            responseBody.error.ErrorMessage = 'This member is not enabled with appropriate permissions'
            responseBody.error.ErrorType = ScreeningErrorType.AUTHENTICATION_ERROR.value
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        else:
            responseBody.error.ErrorType = ScreeningErrorType.SYSTEM_ERROR.value
            responseBody.error.ErrorMessage = 'System Error'
            responseBody.data.timeStamp = \
                _data[ApplicantScreeningConstants.RESPONSE_MESSAGE][TransUnionConstants.GATEWAY][
                    TransUnionConstants.STATUS]['requestDate']
        return DataValidation.createApplicationScreeningResponse(responseBody, responseBody.data,
                                                                 responseBody.data.applicants,
                                                                 responseBody.data.screeningResult,
                                                                 responseBody.error), responseCode

    def getApplicantRetrievalRequestData(self, _applicationData: BaseApplicationRetrievalData, _platformData: dict):
        # creating TransUnionShared Resident Screening Retrieve application API body and header.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}

        _valid, _error = validateRetrieveApplicationRequestData(_applicationData, _platformData)
        if _valid:
            if ApplicantScreeningConstants.APPLICATION_NUMBER not in _applicationData:
                _applicationData.applicationNumber = ' '
            if ApplicantScreeningConstants.REFERENCE_ID not in _applicationData:
                _applicationData.referenceId = ' '

            self.Body = DataValidation.serialize_object(
                RetrieveApplicationPayload(DataValidation.serialize_object
                                           (RetrievalGateway(_platformData[TransUnionConstants.VERSION],
                                                             DataValidation.serialize_object(
                                                                 Agent(_platformData[TransUnionConstants.MEMBER_NAME],
                                                                       _platformData[TransUnionConstants.PASSWORD],
                                                                       _platformData[TransUnionConstants.PROPERTY_ID],
                                                                       _platformData[TransUnionConstants.SOURCE_ID],
                                                                       '')),
                                                             DataValidation.serialize_object(
                                                                 RetrievalApplication(
                                                                     _applicationData.applicationNumber,
                                                                     _applicationData.referenceId))))))

            self.Headers = {'Content-Type': 'text/xml; charset=UTF8',
                            'Accept': 'application/json'}
        else:
            self.Error = {
                ApplicantScreeningConstants.RESPONSE_CODE: ApplicantScreeningConstants.HTTP_BAD_RESPONSE_CODE,
                ApplicantScreeningConstants.RESPONSE_MESSAGE: _error}

        # returning Transunion Resident Screening Create Application API body, headers and parameters
        return dicttoxml.dicttoxml(self.Body, item_func=lambda x: x[:-1], attr_type=False, root=False).decode('utf-8'), \
               self.Headers, self.Params, self.Error
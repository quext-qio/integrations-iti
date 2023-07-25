import base64
import hashlib
import hmac
import json
import logging
import random
from datetime import datetime
from typing import List, Dict, Any

import requests

from ResidentVerificationShared.DataValidation import BaseApplicantData, HTTPRequestType, \
    ResidentVerificationConstants, DataValidation, BaseIdentityEvaluationData, SecurityQuestion, usStateAbbrev, \
    BaseIdentityEvaluationResponse, VerificationErrorType, VerificationStatusType, BaseErrorItem, RiskType, \
    BaseIdentityVerificationResponse, SecurityAnswerItem, SecurityQuestionItem
from ResidentVerificationShared.IntegrationInterface import IntegrationInterface


class AddressPayload:
    StreetAddress: str
    City: str
    State: str
    PostalCode: str
    Country: str
    AddressType: str

    def __init__(self, _streetAddress, _city, _state, _postalCode, _country, _addressType):
        self.StreetAddress = _streetAddress
        self.City = _city
        self.State = _state
        self.PostalCode = _postalCode
        self.Country = _country
        self.AddressType = _addressType


class ApplicantPayload:
    FirstName: str
    LastName: str
    MiddleName: str
    BirthDate: str
    Ssn: str
    Phone: str
    Email: str
    Addresses: List[AddressPayload]

    def __init__(self, _firstName, _lastName, _middleName, _birthDate, _ssn, _phone, _emailAddress, _address):
        self.FirstName = _firstName
        self.LastName = _lastName
        self.MiddleName = _middleName
        self.BirthDate = _birthDate
        self.Ssn = _ssn
        self.Phone = _phone
        self.Email = _emailAddress
        self.Addresses = _address


class IdentityEvaluateAnswer:
    QuestionKeyName: str
    SelectedChoiceKeyName: str

    def __init__(self, _questionKeyName, _selectedChoiceKeyName):
        self.QuestionKeyName = _questionKeyName
        self.SelectedChoiceKeyName = _selectedChoiceKeyName


class IdentityVerificationPayload:
    OrganizationId: str
    ReferenceNumber: str
    Applicant: ApplicantPayload

    def __init__(self, _organizationID, _referenceNumber, _applicant):
        self.OrganizationId = _organizationID
        self.ReferenceNumber = _referenceNumber
        self.Applicant = _applicant


class IdentityEvaluationPayload:
    OrganizationId: str
    ReferenceNumber: str
    Answers: List[IdentityEvaluateAnswer]

    def __init__(self, _organizationID, _referenceNumber, _answers):
        self.OrganizationId = _organizationID
        self.ReferenceNumber = _referenceNumber
        self.Answers = _answers


def getRiskType(_type):
    switcher = {
        'low': RiskType.LOW,
        'high': RiskType.HIGH,
        'medium': RiskType.MODERATE
    }
    return switcher.get(_type, RiskType.NONE)


def sendHTTPRequest(requestType: HTTPRequestType, url: str, _data=None, _auth: dict = None,
                    _header: dict = None):
    response = {}
    if requestType == HTTPRequestType.GET:
        response = requests.get(url, data=_data, auth=_auth, headers=_header)
    else:
        response = requests.post(url, data=_data, auth=_auth, headers=_header)
    return response


def getTransUnionNonceTimeStamp():
    response = sendHTTPRequest(HTTPRequestType.GET, (TransUnionConstants.URL +
                                                     TransUnionConstants.AUTHENTICATION_PATH))
    data = {ResidentVerificationConstants.RESPONSE_CODE: response,
            ResidentVerificationConstants.RESPONSE_MESSAGE: json.loads(response.text)}
    return data


def getMD5HashContent(_data: Dict[str, Any]):
    json_encode = json.dumps(_data)
    base64Encoded = json_encode.encode(TransUnionConstants.ASCII)
    _hash = hashlib.md5()
    _hash.update(base64Encoded)
    contentBase64 = base64.b64encode(_hash.digest())
    return contentBase64.decode(TransUnionConstants.ASCII)


def validateIdentityVerificationResponse(_response: dict, _platformData: dict):
    _response = _response[ResidentVerificationConstants.RESPONSE_MESSAGE]
    responseBody = BaseIdentityVerificationResponse()
    responseBody.data.ReferenceNumber = _response[TransUnionConstants.REFERENCE_NUMBER]
    responseBody.data.VerificationDetails = _response['VerificationDetails']
    responseBody.data.ApplicationNumber = _response['ApplicationNumber']
    responseBody.data.PotentialRisk = getRiskType(_response['RiskIndicator']).value
    responseCode = ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE

    if str(_response[TransUnionConstants.TRANSACTION_STATUS]).upper() == TransUnionConstants.COMPLETED:
        if str(_response[TransUnionConstants.RISK_INDICATOR]).upper() == TransUnionConstants.HIGH:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            responseBody.error.ErrorType = VerificationErrorType.VERIFICATION_ERROR.value
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
        elif len(_response[TransUnionConstants.QUESTIONS]) and str(
                _response[TransUnionConstants.QUESTIONS][0][TransUnionConstants.QUESTION_KEY_NAME]) == \
                TransUnionConstants.IDM_CHOICE:
            _questionData = BaseIdentityEvaluationData()
            _questionData.referenceNumber = _response[TransUnionConstants.REFERENCE_NUMBER]
            _securityQuestionObj = SecurityQuestion()
            _securityQuestionObj.questionKey = TransUnionConstants.IDM_CHOICE
            _securityQuestionObj.answerKey = TransUnionConstants.IDENTITY_VERIFICATION_SECURITY_QUESTIONS
            _questionData.securityQuestions = [_securityQuestionObj]

            _body, _headers, _params, _errorResponse = TransUnionController().getIdentityEvaluationRequestData(
                _questionData, _platformData)

            _res = sendHTTPRequest(HTTPRequestType.POST, (TransUnionConstants.URL +
                                                          TransUnionConstants.EVALUATION_PATH), _body, None, _headers)
            responseBody = {ResidentVerificationConstants.RESPONSE_CODE: _res.status_code,
                            ResidentVerificationConstants.RESPONSE_MESSAGE: json.loads(_res.text)}
            return formatEvaluationResponse(responseBody)

        elif str(_response[TransUnionConstants.RESULT]) == TransUnionConstants.RESULT_STATUS_APPLICANT_QUESTIONED:
            responseBody.data.VerificationStatus = VerificationStatusType.SUCCESS.value
            securityQues = []
            for i in range(len(_response['Questions'])):
                questionKey = _response['Questions'][i]['QuestionKeyName']
                questionDescription = _response['Questions'][i]['QuestionDisplayName']
                answerList = []
                for j in range(len(_response['Questions'][i]['Choices'])):
                    answerList.append(DataValidation.serialize_object(
                        SecurityAnswerItem(_response['Questions'][i]['Choices'][j]['ChoiceKeyName'],
                                           _response['Questions'][i]['Choices'][j]['ChoiceDisplayName'])))

                securityQues.append(DataValidation.serialize_object(
                    SecurityQuestionItem(questionKey, questionDescription, answerList)))
            responseBody.data.SecurityQuestions = securityQues
            responseCode = ResidentVerificationConstants.HTTP_GOOD_RESPONSE_CODE

            responseBody.error.__delattr__('ErrorType')
            responseBody.error.__delattr__('InvalidParameter')

            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
        else:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode


def formatEvaluationResponse(_data: dict):
    responseCode = _data[ResidentVerificationConstants.RESPONSE_CODE]
    data = _data[ResidentVerificationConstants.RESPONSE_MESSAGE]
    responseBody = BaseIdentityVerificationResponse()
    responseBody.data.ReferenceNumber = data[TransUnionConstants.REFERENCE_NUMBER]

    if responseCode == 200:
        responseBody.data.VerificationDetails = data['VerificationDetails']
        responseBody.data.ApplicationNumber = data['ApplicationNumber']
        responseBody.data.PotentialRisk = getRiskType(data['RiskIndicator']).value

        if data[TransUnionConstants.RESULT] == TransUnionConstants.RESULT_STATUS_APPLICANT_QUESTIONED:
            securityQues = []
            for i in range(len(data['Questions'])):
                questionKey = data['Questions'][i]['QuestionKeyName']
                questionDescription = data['Questions'][i]['QuestionDisplayName']
                answerList = []
                for j in range(len(data['Questions'][i]['Choices'])):
                    answerList.append(DataValidation.serialize_object(
                        SecurityAnswerItem(data['Questions'][i]['Choices'][j]['ChoiceKeyName'],
                                           data['Questions'][i]['Choices'][j]['ChoiceDisplayName'])))

                securityQues.append(DataValidation.serialize_object(
                    SecurityQuestionItem(questionKey, questionDescription, answerList)))

            responseBody.data.VerificationStatus = VerificationStatusType.SUCCESS.value
            responseBody.data.SecurityQuestions = securityQues
            responseCode = ResidentVerificationConstants.HTTP_GOOD_RESPONSE_CODE
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
        else:
            responseCode = ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
    elif responseCode == 401:
        responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
        responseBody.error.ErrorType = VerificationErrorType.AUTHENTICATION_ERROR.value
        responseCode = ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE
        return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                         responseBody.error), responseCode
    elif responseCode == 409:
        responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
        responseCode = ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE
        if "ErrorMessages" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE]:
            responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                'ErrorMessages']

        if "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'InvalidInquiry':
            responseBody.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
        elif "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'SystemError':
            responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
        else:
            responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
        return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                         responseBody.error), responseCode

    responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
    responseCode = ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE
    return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                     responseBody.error), responseCode


def validateIdentityVerificationRequestData(_residentData: BaseApplicantData, _platformData: dict):
    responseObj = BaseIdentityVerificationResponse()
    if ResidentVerificationConstants.MIDDLE_NAME not in _residentData:
        _residentData.middleName = ' '
    if 1 <= (len(_residentData.firstName) <= 15 and 1 <= len(_residentData.lastName) <= 25 and 0 <= len(
            _residentData.middleName) <= 15
             and len(_residentData.address.streetAddress) <= 100 and len(_residentData.address.city) <= 27) and \
            DataValidation.validateStringField(_platformData[TransUnionConstants.PROPERTY_ID]) and \
            len(_platformData[TransUnionConstants.SECRET_KEY]) > 0:
        return True, {}
    else:
        responseObj.data.VerificationStatus = VerificationStatusType.FAIL.value
        responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
        if len(_residentData.firstName) > 15:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.FIRST_NAME,
                                       'First Name cannot exceed 15 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_residentData.lastName) > 25:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.LAST_NAME, 'Last Name cannot exceed 25 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_residentData.middleName) > 15:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.MIDDLE_NAME,
                                       'Middle Name cannot exceed 15 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_residentData.address.streetAddress) > 100:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.STREET_ADDRESS,
                                       'Street Address cannot exceed 100 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_residentData.address.city) > 27:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.CITY, 'City cannot exceed 27 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if DataValidation.validateStringField(_platformData[TransUnionConstants.PROPERTY_ID]):
            _errorItem = BaseErrorItem(ResidentVerificationConstants.PLATFORM_DATA, 'Invalid Platform Data')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_platformData[TransUnionConstants.SECRET_KEY]) == 0:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.PLATFORM_DATA, 'Invalid Platform Data')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        return False, DataValidation.createVerificationResponse(responseObj, responseObj.data, responseObj.error)


def validateIdentityEvaluationRequestData(_evaluationData: BaseIdentityEvaluationData, _platformData: dict):
    responseObj = BaseIdentityEvaluationResponse()
    if (8 <= len(_evaluationData.referenceNumber) <= 24) and \
            DataValidation.validateStringField(_platformData[TransUnionConstants.PROPERTY_ID]) and \
            len(_platformData[TransUnionConstants.SECRET_KEY]) > 0:
        return True, {}
    else:
        responseObj.VerificationStatus = VerificationStatusType.FAIL.value
        responseObj.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
        if len(_evaluationData.referenceNumber) > 15:
            _errorItem = BaseErrorItem(TransUnionConstants.REFERENCE_NUMBER,
                                       'ReferenceNUmber contains more than 24 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_evaluationData.referenceNumber) < 8:
            _errorItem = BaseErrorItem(TransUnionConstants.REFERENCE_NUMBER,
                                       'ReferenceNUmber contains less than 8 characters')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if DataValidation.validateStringField(_platformData[TransUnionConstants.PROPERTY_ID]):
            _errorItem = BaseErrorItem(ResidentVerificationConstants.PLATFORM_DATA, 'Invalid Platform Data')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        if len(_platformData[TransUnionConstants.SECRET_KEY]) == 0:
            _errorItem = BaseErrorItem(ResidentVerificationConstants.PLATFORM_DATA, 'Invalid Platform Data')
            responseObj.error.InvalidParameter.append(DataValidation.serialize_object(_errorItem))
        return False, DataValidation.createEvaluationResponse(responseObj, responseObj.data, responseObj.error)


class TransUnionConstants:
    URL = 'https://residentid.transunion.com'
    AUTHENTICATION_PATH = '/api/Authentication'
    EVALUATION_PATH = '/api/Identity/Evaluate'
    TIMESTAMP = 'Timestamp'
    NONCE = 'Nonce'
    ASCII = 'ascii'
    ORGANIZATION_ID = 'OrganizationId'
    PROPERTY_ID = 'verificationPropertyId'
    SECRET_KEY = 'secretKey'
    AUTHORIZATION_HEADER = 'tu-residentid '
    TRANSACTION_STATUS = 'TransactionStatus'
    COMPLETED = 'COMPLETED'
    HIGH = 'HIGH'
    RISK_INDICATOR = 'RiskIndicator'
    QUESTIONS = 'Questions'
    QUESTION_KEY_NAME = 'QuestionKeyName'
    IDM_CHOICE = 'IDM_Choice'
    REFERENCE_NUMBER = 'ReferenceNumber'
    IDENTITY_VERIFICATION_SECURITY_QUESTIONS = 'Security Questions'
    RESULT = 'Result'
    RESULT_STATUS_COMPLETED = 'Completed'
    RESULT_STATUS_FAIL = 'Fail'
    RESULT_STATUS_APPLICANT_QUESTIONED = 'ApplicantQuestioned'
    AUTHORIZATION = 'Authorization'
    FAILURE_NOTES = 'FailureNotes'


class TransUnionController(IntegrationInterface):

    def getIdentityVerificationRequestData(self, _residentData: BaseApplicantData, _platformData: dict):
        """
            @desc: this method will check for the _residentData and returns the body, headers, params
            to verify resident details and the error.
            @param: _residentData which contains the resident information like first name, last name
            and so on, _platformData specific information like token, property ID and secret key.
            @return:the body, headers, params for the resident verification API and the error.
        """
        # creating TransUnion Identity Verification API body and header.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}

        _valid, _error = validateIdentityVerificationRequestData(_residentData, _platformData)
        email = ''
        if ResidentVerificationConstants.EMAIL in _residentData:
            email = _residentData.email
        if _valid:
            _response = getTransUnionNonceTimeStamp()
            timeStamp = str(_response[ResidentVerificationConstants.RESPONSE_MESSAGE][TransUnionConstants.TIMESTAMP])
            nonce = str(_response[ResidentVerificationConstants.RESPONSE_MESSAGE][TransUnionConstants.NONCE])
            self.Body = DataValidation.serialize_object(
                IdentityVerificationPayload(_platformData[TransUnionConstants.PROPERTY_ID],
                                            str(random.randrange(10000000,
                                                                 1000000000)),
                                            DataValidation.serialize_object(
                                                ApplicantPayload(_residentData.firstName,
                                                                 _residentData.lastName,
                                                                 _residentData.middleName,
                                                                 datetime.strptime(_residentData.birthDate,
                                                                                   '%Y/%m/%d').strftime(
                                                                     '%m%d%Y'),
                                                                 _residentData.ssn,
                                                                 _residentData.phone,
                                                                 email, [
                                                                     DataValidation.serialize_object(AddressPayload(
                                                                         _residentData.address.streetAddress,
                                                                         _residentData.address.city,
                                                                         usStateAbbrev[
                                                                             _residentData.address.state.upper()],
                                                                         _residentData.address.postalCode,
                                                                         _residentData.address.postalCode,
                                                                         _residentData.address.addressType))]))))

            # MD5 hash of body
            hashMD5Body = getMD5HashContent(self.Body)
            securityToken = '{}{}{}{}'.format(_platformData[TransUnionConstants.PROPERTY_ID],
                                              timeStamp, nonce, hashMD5Body).encode(TransUnionConstants.ASCII)
            secretKey = _platformData[TransUnionConstants.SECRET_KEY].encode(TransUnionConstants.ASCII)

            # Encrypt the security token with secret key using HMAC SHA256 algorithm
            signature = base64.b64encode(hmac.new(secretKey, securityToken, digestmod=hashlib.sha256).digest())

            self.Headers = {'Content-Type': 'application/json',
                            TransUnionConstants.AUTHORIZATION: TransUnionConstants.AUTHORIZATION_HEADER + '{}:{}:{}:{}'.format(
                                _platformData[TransUnionConstants.PROPERTY_ID],
                                signature.decode(TransUnionConstants.ASCII),
                                timeStamp, nonce)}
        else:
            self.Error = {
                ResidentVerificationConstants.RESPONSE_CODE: ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE,
                ResidentVerificationConstants.RESPONSE_MESSAGE: _error}

        # returning TransUnion Identity Verification API body, headers & parameters
        return json.dumps(self.Body), self.Headers, self.Params, self.Error

    def formatIdentityVerificationResponse(self, _data: dict, _platformData: dict = None):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from Trans-Union regarding resident verification.
            @return: the formatted response and the http response status code.
        """
        logging.info("data {}".format(_data))
        responseBody = BaseIdentityVerificationResponse()
        responseCode = _data[ResidentVerificationConstants.RESPONSE_CODE]
        if responseCode == 200:

            responseBody.data.VerificationStatus = VerificationStatusType.SUCCESS.value
            responseBody.data.ReferenceNumber = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                TransUnionConstants.REFERENCE_NUMBER]
            responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                'VerificationDetails']
            responseBody.data.ApplicationNumber = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                'ApplicationNumber']
            responseBody.data.PotentialRisk = getRiskType(
                _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['RiskIndicator']).value
            return validateIdentityVerificationResponse(_data, _platformData)
        elif responseCode == 401:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE]
            responseBody.error.ErrorType = VerificationErrorType.AUTHENTICATION_ERROR.value
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
        elif responseCode == 409:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            if "ErrorMessages" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE]:
                responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                    'ErrorMessages']

            if "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                    _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'InvalidInquiry':
                responseBody.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
            elif "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                    _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'SystemError':
                responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
            else:
                responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
            return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                             responseBody.error), responseCode
        else:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value

        return DataValidation.createVerificationResponse(responseBody, responseBody.data,
                                                         responseBody.error), responseCode

    def getIdentityEvaluationRequestData(self, _questionsData: BaseIdentityEvaluationData, _platformData: dict):
        """
            @desc: this method will check for the _residentData and returns the body, headers, params
            to verify resident details and the error.
            @param: _residentData which contains the resident information like first name, last name
            and so on, _platformData specific information like token, property ID and secret key.
            @return:the body, headers, params for the resident evaluation API and the error.
        """
        # creating TransUnion Identity Evaluation API body and header.
        self.Error = {}
        self.Params = {}
        self.Body = {}
        self.Headers = {}

        _valid, _error = validateIdentityEvaluationRequestData(_questionsData, _platformData)
        if _valid:
            _response = getTransUnionNonceTimeStamp()
            timeStamp = str(_response[ResidentVerificationConstants.RESPONSE_MESSAGE][TransUnionConstants.TIMESTAMP])
            nonce = str(_response[ResidentVerificationConstants.RESPONSE_MESSAGE][TransUnionConstants.NONCE])

            _answers = []
            for i in range(len(_questionsData.securityQuestions)):
                _answers.append(DataValidation.serialize_object(IdentityEvaluateAnswer(
                    _questionsData.securityQuestions[i].questionKey,
                    _questionsData.securityQuestions[i].answerKey)))

            self.Body = DataValidation.serialize_object(
                IdentityEvaluationPayload(_platformData[TransUnionConstants.PROPERTY_ID],
                                          _questionsData.referenceNumber, _answers))
            # MD5 hash of body
            hashMD5Body = getMD5HashContent(self.Body)
            securityToken = '{}{}{}{}'.format(_platformData[TransUnionConstants.PROPERTY_ID],
                                              timeStamp, nonce, hashMD5Body).encode(TransUnionConstants.ASCII)
            secretKey = _platformData[TransUnionConstants.SECRET_KEY].encode(TransUnionConstants.ASCII)

            # Encrypt the security token with secret key using HMAC SHA256 algorithm
            signature = base64.b64encode(hmac.new(secretKey, securityToken, digestmod=hashlib.sha256).digest())

            self.Headers = {'Content-Type': 'application/json',
                            'Authorization': TransUnionConstants.AUTHORIZATION_HEADER + '{}:{}:{}:{}'.format(
                                _platformData[TransUnionConstants.PROPERTY_ID],
                                signature.decode(TransUnionConstants.ASCII),
                                timeStamp, nonce)}

        else:
            self.Error = {
                ResidentVerificationConstants.RESPONSE_CODE: ResidentVerificationConstants.HTTP_BAD_RESPONSE_CODE,
                ResidentVerificationConstants.RESPONSE_MESSAGE: _error}

        # returning TransUnion Identity Verification API body, headers & parameters
        return json.dumps(self.Body), self.Headers, self.Params, self.Error

    def formatIdentityEvaluationResponse(self, _data: dict, _platformData: dict = None):
        """
            @desc: this method will check for the _data and returns the formatted response and the http response status
            code
            @param: _data which contains the response returned from Trans-Union regarding resident evaluation.
            @return: the formatted response and the http response status code.
        """
        logging.info("data {}".format(_data))
        responseBody = BaseIdentityEvaluationResponse()
        responseBody.data.ReferenceNumber = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
            TransUnionConstants.REFERENCE_NUMBER]
        responseCode = _data[ResidentVerificationConstants.RESPONSE_CODE]

        if responseCode == 200:
            responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                'VerificationDetails']
            responseBody.data.ApplicationNumber = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                'ApplicationNumber']
            responseBody.data.PotentialRisk = getRiskType(
                _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['RiskIndicator']).value

            if _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                TransUnionConstants.RESULT] == TransUnionConstants.RESULT_STATUS_COMPLETED:
                responseBody.data.VerificationStatus = VerificationStatusType.SUCCESS.value
                responseBody.error.__delattr__('ErrorType')
                responseBody.error.__delattr__('InvalidParameter')
            elif _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                TransUnionConstants.RESULT] == TransUnionConstants.RESULT_STATUS_FAIL:
                responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
                responseBody.error.ErrorType = VerificationErrorType.AUTHENTICATION_ERROR.value
            else:
                responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
                responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
            return DataValidation.createEvaluationResponse(responseBody, responseBody.data,
                                                           responseBody.error), responseCode
        elif responseCode == 409:
            responseBody.data.VerificationStatus = VerificationStatusType.FAIL.value
            if "ErrorMessages" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE]:
                responseBody.data.VerificationDetails = _data[ResidentVerificationConstants.RESPONSE_MESSAGE][
                    'ErrorMessages']
            if "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                    _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'InvalidInquiry':
                responseBody.error.ErrorType = VerificationErrorType.VALIDATION_ERROR.value
            elif "ErrorType" in _data[ResidentVerificationConstants.RESPONSE_MESSAGE] and \
                    _data[ResidentVerificationConstants.RESPONSE_MESSAGE]['ErrorType'] == 'SystemError':
                responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
            else:
                responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value
            return DataValidation.createEvaluationResponse(responseBody, responseBody.data,
                                                           responseBody.error), responseCode
        else:
            responseBody.error.ErrorType = VerificationErrorType.SYSTEM_ERROR.value

        return DataValidation.createEvaluationResponse(responseBody, responseBody.data,
                                                       responseBody.error), responseCode

import json

from PeriodicShared.Config.Config import Config
from PeriodicShared.Controller.MessageNotificationController import MessageNotificationController
from PeriodicShared.Model.Periodic import Periodic
from PeriodicShared.Model.PeriodicResponse import BaseResponse, Bookable
from PeriodicShared.Utilities.Convert import Convert
from PeriodicShared.Utilities.DataValidation import Validate, Schema, constructAvailabilityObj, validateAvailability, \
    convertPeriodicAvailability
from PeriodicShared.Utilities.HTTPHelper import sendRequest, HTTPRequest
from PeriodicShared.Utilities.PeriodicConstants import PeriodicConstants


class BookableConstants:
    BOOKABLE_NAME = 'Schedule a tour to view units at '
    BOOKABLE_DATA = 'bookableData'
    APPOINTMENT_DURATION = 'appointmentDuration'
    APPOINTMENT_FREQUENCY = 'appointmentFrequency'
    SENDER_EMAIL = 'senderEmail'
    MESSAGING_NOTIFICATION = "messagenotifications"
    PARAMS = 'params'
    DURATION = 'duration'
    FREQUENCY = 'frequency'
    CUSTOM_LINK = 'customlink'
    NEW_AVAILABILITY = 'newavailability'
    REQUIRED_RESOURCES = 'requiredresources'


class BookableController:
    @staticmethod
    def deleteBookable(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        _body = Periodic.deleteBookable()
        # Required Field
        _body.params.id = _data[PeriodicConstants.ID]

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        return _body, _header, _error

    @staticmethod
    def updateBookable(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        isValid, error = Validate.schema(Schema.UPDATE_BOOKABLE, _data)
        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        _body = Convert.toDict(Periodic.updateBookable())
        # Required Fields
        _body[PeriodicConstants.PARAMS][PeriodicConstants.ID] = _data[PeriodicConstants.ID]

        # Optional Fields
        if PeriodicConstants.NAME in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.NAME] = _data[PeriodicConstants.NAME]
        if PeriodicConstants.RESOURCE_ID in _data:
            _body[PeriodicConstants.PARAMS][BookableConstants.REQUIRED_RESOURCES] = _data[PeriodicConstants.RESOURCE_ID]
        if PeriodicConstants.AVAILABILITY in _data:
            _availability = []
            if PeriodicConstants.MONDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.MONDAY], PeriodicConstants.MONDAY)
            if PeriodicConstants.TUESDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.TUESDAY], PeriodicConstants.TUESDAY)
            if PeriodicConstants.WEDNESDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.WEDNESDAY],
                    PeriodicConstants.WEDNESDAY)
            if PeriodicConstants.THURSDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.THURSDAY],
                    PeriodicConstants.THURSDAY)
            if PeriodicConstants.FRIDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.FRIDAY], PeriodicConstants.FRIDAY)
            if PeriodicConstants.SATURDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.SATURDAY],
                    PeriodicConstants.SATURDAY)
            if PeriodicConstants.SUNDAY in _data[PeriodicConstants.AVAILABILITY]:
                _availability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.SUNDAY], PeriodicConstants.SUNDAY)
            _body[PeriodicConstants.PARAMS][BookableConstants.NEW_AVAILABILITY] = _availability
        if BookableConstants.APPOINTMENT_DURATION in _data:
            _body[PeriodicConstants.PARAMS][BookableConstants.DURATION] = int(
                _data[BookableConstants.APPOINTMENT_DURATION]) * 60
        if BookableConstants.APPOINTMENT_FREQUENCY in _data:
            _body[PeriodicConstants.PARAMS][BookableConstants.FREQUENCY] = int(
                _data[BookableConstants.APPOINTMENT_FREQUENCY]) * 60

        return _body, _header, _error

    @staticmethod
    def createBookable(_data: dict, jwtToken: dict, _dataValidated: bool = False):

        bookableData = _data[BookableConstants.BOOKABLE_DATA]
        _body, _header, _error = {}, {}, {}

        if not _dataValidated:
            isValid, error = Validate.schema(Schema.CREATE_BOOKABLE, bookableData)

            isValidBookableData, errorBookableData = validateAvailability(
                bookableData[PeriodicConstants.AVAILABILITY], BookableConstants.BOOKABLE_DATA)
            if not isValidBookableData:
                isValid = False
                error.update(errorBookableData)

            if not isValid:
                response = BaseResponse()
                response.error = error
                return {}, {}, Convert.toJson(response)

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        _body = Periodic.createBookable()

        # Required Fields
        _body.params.name = BookableConstants.BOOKABLE_NAME + bookableData[PeriodicConstants.COMMUNITY_NAME] + '!'
        _body.params.provider = bookableData[PeriodicConstants.COMMUNITY_ID]
        _body.params.requiredresources = bookableData[PeriodicConstants.RESOURCE_ID]
        _body.params.forms = [Periodic.createForm(Config.formID)]

        # Build New Availability Field
        _body.params.newavailability = []
        if PeriodicConstants.AVAILABILITY in bookableData:
            if PeriodicConstants.MONDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.MONDAY], PeriodicConstants.MONDAY)
            if PeriodicConstants.TUESDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.TUESDAY], PeriodicConstants.TUESDAY)
            if PeriodicConstants.WEDNESDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.WEDNESDAY],
                    PeriodicConstants.WEDNESDAY)
            if PeriodicConstants.THURSDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.THURSDAY],
                    PeriodicConstants.THURSDAY)
            if PeriodicConstants.FRIDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.FRIDAY], PeriodicConstants.FRIDAY)
            if PeriodicConstants.SATURDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.SATURDAY],
                    PeriodicConstants.SATURDAY)
            if PeriodicConstants.SUNDAY in bookableData[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    bookableData[PeriodicConstants.AVAILABILITY][PeriodicConstants.SUNDAY], PeriodicConstants.SUNDAY)

        # Optional Fields
        if BookableConstants.APPOINTMENT_DURATION in bookableData:
            _body.params.duration = int(bookableData[BookableConstants.APPOINTMENT_DURATION]) * 60
        if BookableConstants.APPOINTMENT_FREQUENCY in bookableData:
            _body.params.frequency = int(bookableData[BookableConstants.APPOINTMENT_FREQUENCY]) * 60
        res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
        isValid, bookableOutput = BookableController.formatBookableResponse(res.status_code,
                                                                            json.loads(res.text),
                                                                            Schema.CREATE_BOOKABLE)

        if not isValid:
            return False, Convert.toJson(bookableOutput)

        # Construct createDefaultNotification parameters.
        messageData = {
            PeriodicConstants.SENDER: bookableData[BookableConstants.SENDER_EMAIL],
            PeriodicConstants.SMS_TEMPLATE: Config.smsTemplateID,
            PeriodicConstants.EMAIL_TEMPLATE: Config.emailTemplateID,
            PeriodicConstants.PROVIDER: bookableData[PeriodicConstants.COMMUNITY_ID],
            PeriodicConstants.BOOKABLE_ID: bookableOutput.data.id
        }

        isValid, output = MessageNotificationController.createDefaultNotification(messageData, jwtToken)

        if not isValid:
            return False, Convert.toJson(output)
        return True, Convert.toJson(bookableOutput)

    @staticmethod
    def getBookable(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        isValid, error = Validate.schema(Schema.GET_BOOKABLE, _data)
        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response
        _body = Periodic.getBookable()
        _body.params.provider = _data[PeriodicConstants.COMMUNITY_ID]

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        return _body, _header, _error

    @staticmethod
    def formatBookableResponse(responseCode, responseData: dict, _type: Schema):
        response = BaseResponse()
        if responseCode == 200:
            # Constructing Resource Part of the Response
            if _type == Schema.GET_BOOKABLE:
                if len(responseData[PeriodicConstants.RESULT]) == 0:
                    response.data = {BookableConstants.BOOKABLE_DATA: "no records of bookable found"}
                else:
                    bookable = Bookable()
                    bookable.name = responseData[PeriodicConstants.RESULT][0][PeriodicConstants.NAME]
                    bookable.id = responseData[PeriodicConstants.RESULT][0][PeriodicConstants.ID]
                    bookable.modified = responseData[PeriodicConstants.RESULT][0][PeriodicConstants.MODIFIED]
                    bookable.communityID = responseData[PeriodicConstants.RESULT][0][PeriodicConstants.PROVIDER_ID]
                    bookable.appointmentDuration = responseData[PeriodicConstants.RESULT][0][BookableConstants.DURATION]
                    bookable.appointmentFrequency = responseData[PeriodicConstants.RESULT][0][
                        BookableConstants.FREQUENCY]
                    bookable.description = responseData[PeriodicConstants.RESULT][0][PeriodicConstants.DESCRIPTION]
                    bookable.customLink = responseData[PeriodicConstants.RESULT][0][BookableConstants.CUSTOM_LINK]
                    bookable.availability = convertPeriodicAvailability(
                        responseData[PeriodicConstants.RESULT][0][BookableConstants.NEW_AVAILABILITY])
                    response.data = bookable
            elif _type == Schema.UPDATE_BOOKABLE:
                bookable = Bookable()
                bookable.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
                bookable.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
                bookable.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
                bookable.communityID = responseData[PeriodicConstants.RESULT][PeriodicConstants.PROVIDER_ID]
                bookable.appointmentDuration = responseData[PeriodicConstants.RESULT][BookableConstants.DURATION]
                bookable.appointmentFrequency = responseData[PeriodicConstants.RESULT][BookableConstants.FREQUENCY]
                bookable.description = responseData[PeriodicConstants.RESULT][PeriodicConstants.DESCRIPTION]
                bookable.customLink = responseData[PeriodicConstants.RESULT][BookableConstants.CUSTOM_LINK]
                bookable.availability = convertPeriodicAvailability(
                    responseData[PeriodicConstants.RESULT][BookableConstants.NEW_AVAILABILITY])
                response.data = bookable

            elif _type == Schema.DELETE_BOOKABLE:
                response.data = {PeriodicConstants.ID: responseData[PeriodicConstants.RESULT][PeriodicConstants.ID],
                                 PeriodicConstants.MESSAGE: "bookable deleted."}
            return True, response
        elif responseCode == 201:
            # Constructing Bookable Part of the Response
            bookable = Bookable()
            bookable.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
            bookable.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
            bookable.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
            bookable.communityID = responseData[PeriodicConstants.RESULT][PeriodicConstants.PROVIDER_ID]
            bookable.appointmentDuration = responseData[PeriodicConstants.RESULT][BookableConstants.DURATION]
            bookable.appointmentFrequency = responseData[PeriodicConstants.RESULT][BookableConstants.FREQUENCY]
            bookable.description = responseData[PeriodicConstants.RESULT][PeriodicConstants.DESCRIPTION]
            bookable.customLink = responseData[PeriodicConstants.RESULT][BookableConstants.CUSTOM_LINK]
            bookable.availability = convertPeriodicAvailability(
                responseData[PeriodicConstants.RESULT][BookableConstants.NEW_AVAILABILITY])
            response.data = bookable
            return True, response
        elif responseCode == 409:
            response.error = {
                BookableConstants.BOOKABLE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 401:
            response.error = {
                BookableConstants.BOOKABLE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 404:
            if "provider not found" in responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]:
                response.error = {BookableConstants.BOOKABLE_DATA: "community not found"}
            else:
                response.error = {
                    BookableConstants.BOOKABLE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 500:
            response.error = {
                BookableConstants.BOOKABLE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.DATA]}
            return False, response
        else:
            response.error = {
                BookableConstants.BOOKABLE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response

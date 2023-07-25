import json

from PeriodicShared.Model.Periodic import Periodic
from PeriodicShared.Model.PeriodicResponse import BaseResponse
from PeriodicShared.Utilities.Convert import Convert
from PeriodicShared.Utilities.HTTPHelper import sendRequest, HTTPRequest
from PeriodicShared.Utilities.PeriodicConstants import PeriodicConstants


class MessageNotificationConstants:
    MESSAGING_NOTIFICATION = "messagenotifications"


class MessageNotificationController:
    @staticmethod
    def createDefaultNotification(_data: dict, _jwtToken: dict):
        response = BaseResponse()
        notificationCreated = True
        response.error[MessageNotificationConstants.MESSAGING_NOTIFICATION] = []
        _body, _header, _errorResponse = MessageNotificationController.createMessagingNotification(
            _data, _jwtToken, "email"
        )
        res = sendRequest(HTTPRequest.POST, _body, '', _header)
        isValid, output = MessageNotificationController.formatCreateMessagingNotification(res.status_code,
                                                                                          json.loads(res.text))
        if not output.data:
            notificationCreated = False
            response.error[MessageNotificationConstants.MESSAGING_NOTIFICATION].append(output.error)

        _body, _header, _errorResponse = MessageNotificationController.createMessagingNotification(
            _data, _jwtToken, "sms"
        )
        res = sendRequest(HTTPRequest.POST, _body, '', _header)
        isValid, output = MessageNotificationController.formatCreateMessagingNotification(res.status_code,
                                                                                          json.loads(res.text))
        if not output.data:
            notificationCreated = False
            response.error[MessageNotificationConstants.MESSAGING_NOTIFICATION].append(output.error)

        return notificationCreated, response

    @staticmethod
    def createMessagingNotification(_data: dict, _jwtToken: dict, _type):
        _body, _header, _error = {}, {}, {}
        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(_jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   _jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   _jwtToken[PeriodicConstants.JWT_KEY])}
        # Required Fields
        _body = Periodic.createMessageNotification()
        _body.params.sender = _data[PeriodicConstants.SENDER]
        if _type == "sms":
            _body.params.template = _data[PeriodicConstants.SMS_TEMPLATE]
        else:
            _body.params.template = _data[PeriodicConstants.EMAIL_TEMPLATE]
        _body.params.type = "notification"
        _body.params.provider = _data[PeriodicConstants.PROVIDER]
        _body.params.messagetype = _type
        _body.params.bookable_id = _data[PeriodicConstants.BOOKABLE_ID]
        return Convert.toJson(_body), _header, _error

    @staticmethod
    def formatCreateMessagingNotification(responseCode, responseData: dict):
        response = BaseResponse()
        if responseCode == 201:
            # Constructing Messaging Notification Part of the Response
            response.data = responseData[PeriodicConstants.RESULT][MessageNotificationConstants.MESSAGING_NOTIFICATION]
            return True, response
        else:
            response.error = {
                PeriodicConstants.PLATFORM_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response

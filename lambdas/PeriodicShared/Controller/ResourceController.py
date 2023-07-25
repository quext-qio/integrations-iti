import json
import logging

from PeriodicShared.Model.Periodic import Periodic
from PeriodicShared.Model.PeriodicResponse import BaseResponse, Resource
from PeriodicShared.Utilities.Convert import Convert
from PeriodicShared.Utilities.DataValidation import Validate, Schema, constructAvailabilityObj, validateAvailability, \
    convertPeriodicAvailability
from PeriodicShared.Utilities.HTTPHelper import sendRequest, HTTPRequest
from PeriodicShared.Utilities.PeriodicConstants import PeriodicConstants


class ResourceConstants:
    RESOURCE_DATA = "resourceData"
    ASSOCIATED_PROVIDERS = "associated_providers"
    NEW_AVAILABILITY = 'newavailability'
    PHONE_NUMBER = 'phonenumber'


class ResourceController:
    @staticmethod
    def createProviderResource(_data: list, jwtToken: dict, _dataValidated: bool = False):
        response = BaseResponse()
        response.data[ResourceConstants.RESOURCE_DATA] = []
        _isValid = False
        for resourceItem in _data:
            _body, _header, _errorResponse = ResourceController.createResource(
                resourceItem, jwtToken, _dataValidated)
            if not _body:
                response.error[PeriodicConstants.NAME] = resourceItem[PeriodicConstants.NAME]
                response.error[PeriodicConstants.NAME] = _errorResponse.error
                continue
            res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
            isValid, output = ResourceController.formatResourceResponse(res.status_code, json.loads(res.text),
                                                                        Schema.CREATE_RESOURCE)
            if isValid:
                _isValid = True
                response.data[ResourceConstants.RESOURCE_DATA].append(output.data)
            else:
                response.error[PeriodicConstants.NAME] = resourceItem[PeriodicConstants.NAME]
                response.error[PeriodicConstants.NAME] = output.error[PeriodicConstants.PLATFORM_DATA]

        return _isValid, response

    @staticmethod
    def createResource(_data: dict, jwtToken: dict, _dataValidated: bool = False):
        _body, _header, _error = {}, {}, {}

        if not _dataValidated:
            # Validate _data for Update Schema
            isValid, error = Validate.schema(Schema.CREATE_RESOURCE, _data)

            # Special Validation case for AVAILABILITY. Check if all start time is less than end time.
            isValidLeasingData, errorLeasingData = validateAvailability(
                _data[PeriodicConstants.AVAILABILITY], ResourceConstants.RESOURCE_DATA)
            if not isValidLeasingData:
                isValid = False
                error.update(errorLeasingData)
            if not isValid:
                response = BaseResponse()
                response.error = error
                return {}, {}, response

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        # Required Fields
        _body = Periodic.createResource()
        _body.params.name = _data[PeriodicConstants.NAME]
        _body.params.timezone = _data[PeriodicConstants.TIMEZONE]
        _body.params.type = "resource"
        _body.params.providers.append(_data[PeriodicConstants.COMMUNITY_ID])

        # Build New Availability Field
        _body.params.newavailability = []
        if PeriodicConstants.AVAILABILITY in _data:
            if PeriodicConstants.MONDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.MONDAY], PeriodicConstants.MONDAY)
            if PeriodicConstants.TUESDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.TUESDAY], PeriodicConstants.TUESDAY)
            if PeriodicConstants.WEDNESDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.WEDNESDAY],
                    PeriodicConstants.WEDNESDAY)
            if PeriodicConstants.THURSDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.THURSDAY],
                    PeriodicConstants.THURSDAY)
            if PeriodicConstants.FRIDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.FRIDAY], PeriodicConstants.FRIDAY)
            if PeriodicConstants.SATURDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.SATURDAY],
                    PeriodicConstants.SATURDAY)
            if PeriodicConstants.SUNDAY in _data[PeriodicConstants.AVAILABILITY]:
                _body.params.newavailability += constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.SUNDAY], PeriodicConstants.SUNDAY)

        # Optional Fields
        if PeriodicConstants.DESCRIPTION in _data:
            _body.params.description = _data[PeriodicConstants.DESCRIPTION]
        if PeriodicConstants.PHONE in _data:
            _body.params.phonenumber = _data[PeriodicConstants.PHONE]
        if PeriodicConstants.URL in _data:
            _body.params.url = _data[PeriodicConstants.URL]
        return _body, _header, _error

    @staticmethod
    def updateResource(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}

        # Validate _data for Update Schema
        isValid, error = Validate.schema(Schema.UPDATE_RESOURCE, _data)
        isValidLeasingData, errorLeasingData = True, {}

        # Special Validation case for AVAILABILITY. Check if all start time is less than end time.
        if PeriodicConstants.AVAILABILITY in _data:
            isValidLeasingData, errorLeasingData = validateAvailability(
                _data[PeriodicConstants.AVAILABILITY], ResourceConstants.RESOURCE_DATA)
        if not isValidLeasingData:
            isValid = False
            error.update(errorLeasingData)
        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        # Required Fields
        _body = Convert.toDict(Periodic.updateResource())
        _body[PeriodicConstants.PARAMS][PeriodicConstants.ID] = _data[PeriodicConstants.ID]

        # Optional Fields
        if PeriodicConstants.NAME in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.NAME] = _data[PeriodicConstants.NAME]

        if PeriodicConstants.TIMEZONE in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.TIMEZONE] = _data[PeriodicConstants.TIMEZONE]

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
            _body[PeriodicConstants.PARAMS][ResourceConstants.NEW_AVAILABILITY] = _availability

        if PeriodicConstants.DESCRIPTION in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.DESCRIPTION] = _data[PeriodicConstants.DESCRIPTION]
        if PeriodicConstants.PHONE in _data:
            _body[PeriodicConstants.PARAMS]['phonenumber'] = _data[PeriodicConstants.PHONE]
        if PeriodicConstants.URL in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.URL] = _data[PeriodicConstants.URL]
        return _body, _header, _error

    @staticmethod
    def getResource(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        isValid, error = Validate.schema(Schema.GET_RESOURCE, _data)
        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response

        _body = Periodic.getResource()
        # Required Field
        _body.params.provider = _data[PeriodicConstants.COMMUNITY_ID]

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        return _body, _header, _error

    @staticmethod
    def deleteResource(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        isValid, error = Validate.schema(Schema.DELETE_RESOURCE, _data)
        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response

        _body = Periodic.deleteResource()
        # Required Field
        _body.params.id = _data[PeriodicConstants.ID]
        _body.params.provider = _data[PeriodicConstants.COMMUNITY_ID]

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        return _body, _header, _error

    @staticmethod
    def deleteProviderResource(_data: dict, jwtToken: dict):
        response = BaseResponse()
        response.data[ResourceConstants.RESOURCE_DATA] = []
        _isValid = False

        for _resource in _data[PeriodicConstants.RESOURCE_ID]:
            resourceData = {PeriodicConstants.COMMUNITY_ID: _data[PeriodicConstants.COMMUNITY_ID],
                            PeriodicConstants.ID: _resource}
            _body, _header, _errorResponse = ResourceController.deleteResource(resourceData, jwtToken)
            res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
            # Format GetBookable API response
            isValid, output = ResourceController.formatResourceResponse(res.status_code, json.loads(res.text),
                                                                        Schema.DELETE_RESOURCE)
            if not isValid:
                _isValid = False
                response.error.update(output.error)
            else:
                _isValid = True
                response.data[ResourceConstants.RESOURCE_DATA].append(output.data)
        return _isValid, response

    @staticmethod
    def formatResourceResponse(responseCode, responseData: dict, _type: Schema):
        response = BaseResponse()
        if responseCode == 200:
            # Constructing Resource Part of the Response
            if _type == Schema.GET_RESOURCE:
                if len(responseData[PeriodicConstants.RESULT]) == 0:
                    response.data = {ResourceConstants.RESOURCE_DATA: "no records of resource found"}
                else:
                    resourceList = []
                    for item in responseData[PeriodicConstants.RESULT]:
                        resource = Resource()
                        resource.name = item[PeriodicConstants.NAME]
                        resource.id = item[PeriodicConstants.ID]
                        resource.modified = item[PeriodicConstants.MODIFIED]
                        resource.availability = convertPeriodicAvailability(item[ResourceConstants.NEW_AVAILABILITY])
                        if ResourceConstants.ASSOCIATED_PROVIDERS in item:
                            resource.communityID = ''.join(item[ResourceConstants.ASSOCIATED_PROVIDERS])
                        resource.phone = item[ResourceConstants.PHONE_NUMBER]
                        resource.timezone = item[PeriodicConstants.TIMEZONE]
                        resource.url = item[PeriodicConstants.URL]
                        resourceList.append(resource)

                    response.data = resourceList
            elif _type == Schema.UPDATE_RESOURCE:
                resource = Resource()
                resource.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
                resource.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
                resource.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
                resource.availability = convertPeriodicAvailability(
                    responseData[PeriodicConstants.RESULT][ResourceConstants.NEW_AVAILABILITY])
                if ResourceConstants.ASSOCIATED_PROVIDERS in responseData[PeriodicConstants.RESULT]:
                    resource.communityID = ''.join(
                        responseData[PeriodicConstants.RESULT][ResourceConstants.ASSOCIATED_PROVIDERS])
                resource.phone = responseData[PeriodicConstants.RESULT][ResourceConstants.PHONE_NUMBER]
                resource.timezone = responseData[PeriodicConstants.RESULT][PeriodicConstants.TIMEZONE]
                resource.url = responseData[PeriodicConstants.RESULT][PeriodicConstants.URL]
                response.data = resource
            elif _type == Schema.DELETE_RESOURCE:
                response.data = {PeriodicConstants.ID: responseData[PeriodicConstants.RESULT][PeriodicConstants.ID],
                                 PeriodicConstants.MESSAGE: "resource deleted."}
            return True, response
        if responseCode == 201:
            # Constructing Resource Part of the Response
            resource = Resource()
            resource.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
            resource.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
            resource.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
            resource.availability = convertPeriodicAvailability(
                responseData[PeriodicConstants.RESULT][ResourceConstants.NEW_AVAILABILITY])
            resource.communityID = ''.join(
                responseData[PeriodicConstants.RESULT][ResourceConstants.ASSOCIATED_PROVIDERS])
            resource.phone = responseData[PeriodicConstants.RESULT][ResourceConstants.PHONE_NUMBER]
            resource.timezone = responseData[PeriodicConstants.RESULT][PeriodicConstants.TIMEZONE]
            resource.url = responseData[PeriodicConstants.RESULT][PeriodicConstants.URL]
            response.data = resource
            return True, response
        elif responseCode == 409:
            response.error = {
                ResourceConstants.RESOURCE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 401:
            response.error = {
                ResourceConstants.RESOURCE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 404:
            if "provider not found" in responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]:
                response.error = {ResourceConstants.RESOURCE_DATA: "community not found"}
            else:
                response.error = {
                    ResourceConstants.RESOURCE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 500:
            response.error = {
                ResourceConstants.RESOURCE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        else:
            response.error = {
                ResourceConstants.RESOURCE_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response

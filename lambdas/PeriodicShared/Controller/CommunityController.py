import datetime
import json

from PeriodicShared.Controller.BookableController import BookableController
from PeriodicShared.Controller.ResourceController import ResourceController
from PeriodicShared.Model.Periodic import Periodic
from PeriodicShared.Model.PeriodicResponse import BaseResponse, Community
from PeriodicShared.Utilities.Convert import Convert
from PeriodicShared.Utilities.DataValidation import Validate, Schema, validateAvailability
from PeriodicShared.Utilities.HTTPHelper import sendRequest, HTTPRequest
from PeriodicShared.Utilities.PeriodicConstants import PeriodicConstants


class CommunityConstants:
    COMMUNITY_DATA = "communityData"
    BOOKABLE_DATA = "bookableData"
    LEASING_DATA = "resourceData"
    COMMUNITY_NAME = "communityName"
    EMAIL = "email"
    REPLY_EMAIL = "replyEmail"
    INTERNAL_CODE = "internalCode"
    FACEBOOK = "facebookURL"
    TWITTER = "twitterURL"
    INSTAGRAM = "instagramURL"
    PINTREST = "pinterestURL"
    SUBDOMAIN = 'subDomain'
    WEBSITE = 'website'


class CommunityController:
    @staticmethod
    def createCommunity(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        response = BaseResponse()

        isValid, error = Validate.schema(Schema.CREATE_COMMUNITY, _data)

        # Validate availability data
        if ('start' not in error) and ('end' not in error):
            # Validate Community availability data
            isValidCommunityData, errorCommunityData = validateAvailability(
                _data[CommunityConstants.COMMUNITY_DATA][PeriodicConstants.AVAILABILITY],
                CommunityConstants.COMMUNITY_DATA)
            if not isValidCommunityData:
                isValid = False
                error.update(errorCommunityData)

            # Validate Bookable availability data
            isValidBookableData, errorBookableData = validateAvailability(
                _data[CommunityConstants.BOOKABLE_DATA][PeriodicConstants.AVAILABILITY],
                CommunityConstants.BOOKABLE_DATA)
            if not isValidBookableData:
                isValid = False
                error.update(errorBookableData)

            # Validate Resource availability data
            resourceName = []
            for item in _data[CommunityConstants.LEASING_DATA]:
                if item[PeriodicConstants.NAME] in resourceName and PeriodicConstants.RESOURCE_NAME not in error:
                    isValid = False
                    resourceError = {PeriodicConstants.RESOURCE_NAME: 'two or more resource name cannot be same'}
                    error.update(resourceError)

                resourceName.append(item[PeriodicConstants.NAME])
                isValidLeasingData, errorLeasingData = validateAvailability(
                    item[PeriodicConstants.AVAILABILITY], CommunityConstants.LEASING_DATA)
                if (not isValidLeasingData) and CommunityConstants.LEASING_DATA not in error:
                    isValid = False
                    error.update(errorLeasingData)

        if not isValid:
            response.error = error
            return False, Convert.toJson(response)

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        communityData = _data[CommunityConstants.COMMUNITY_DATA]
        _body = Periodic.createProvider()

        # Required Fields
        _body.params.name = communityData[CommunityConstants.COMMUNITY_NAME]
        _body.params.subdomain = communityData[CommunityConstants.SUBDOMAIN]
        _body.params.timezone = communityData[PeriodicConstants.TIMEZONE]
        _body.params.email = communityData[CommunityConstants.EMAIL]
        _body.params.replyto = communityData[CommunityConstants.REPLY_EMAIL]
        _body.params.phone = communityData[PeriodicConstants.PHONE]

        # Build Business Hour Field
        _body.params.businesshours[PeriodicConstants.FRIDAY] = []
        _body.params.businesshours[PeriodicConstants.MONDAY] = []
        _body.params.businesshours[PeriodicConstants.SATURDAY] = []
        _body.params.businesshours[PeriodicConstants.SUNDAY] = []
        _body.params.businesshours[PeriodicConstants.THURSDAY] = []
        _body.params.businesshours[PeriodicConstants.TUESDAY] = []
        _body.params.businesshours[PeriodicConstants.WEDNESDAY] = []
        if PeriodicConstants.FRIDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.FRIDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.FRIDAY])
        if PeriodicConstants.MONDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.MONDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.MONDAY])
        if PeriodicConstants.SATURDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.SATURDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.SUNDAY])
        if PeriodicConstants.THURSDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.THURSDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.THURSDAY])
        if PeriodicConstants.TUESDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.TUESDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.TUESDAY])
        if PeriodicConstants.WEDNESDAY in communityData[PeriodicConstants.AVAILABILITY]:
            _body.params.businesshours[PeriodicConstants.WEDNESDAY] = CommunityController.constructAvailabilityObj(
                communityData[PeriodicConstants.AVAILABILITY][PeriodicConstants.WEDNESDAY])

        # Optional Field
        if PeriodicConstants.ADDRESS in communityData:
            _body.params.address = communityData[PeriodicConstants.ADDRESS][PeriodicConstants.STREET_ADDRESS]
            _body.params.city = communityData[PeriodicConstants.ADDRESS][PeriodicConstants.CITY]
            _body.params.state = communityData[PeriodicConstants.ADDRESS][PeriodicConstants.STATE]
            _body.params.country = communityData[PeriodicConstants.ADDRESS][PeriodicConstants.COUNTRY]
            _body.params.zip = communityData[PeriodicConstants.ADDRESS][PeriodicConstants.POSTAL_CODE]
        if PeriodicConstants.DESCRIPTION in communityData:
            _body.params.description = communityData[PeriodicConstants.DESCRIPTION]
        if CommunityConstants.FACEBOOK in communityData:
            _body.params.facebook = communityData[CommunityConstants.FACEBOOK]
        if CommunityConstants.INSTAGRAM in communityData:
            _body.params.instagram = communityData[CommunityConstants.INSTAGRAM]
        if CommunityConstants.PINTREST in communityData:
            _body.params.pintrest = communityData[CommunityConstants.PINTREST]
        if CommunityConstants.WEBSITE in communityData:
            _body.params.url = communityData[CommunityConstants.WEBSITE]
        _body.params.internalCode = communityData[CommunityConstants.INTERNAL_CODE]

        res = sendRequest(HTTPRequest.POST, json.dumps(Convert.toDict(_body)), '', _header)
        isValid, output = CommunityController.formatCommunityResponse(res.status_code, json.loads(res.text),
                                                                      Schema.CREATE_COMMUNITY)

        """
        # Testing Purpose
        isValid, output = True, {
            "name": "Test name",
            "id": "24b9fdd2d404ff35cfd39887449eb30b",
            "created": "2021-04-14 18:42:20",
            "internalCode": ""
        }
        # Testing Purpose
        """
        if not isValid:
            return False, Convert.toJson(output)

        response.data[PeriodicConstants.COMMUNITY] = output.data

        # Construct createGroupResource parameters.
        for item in _data[CommunityConstants.LEASING_DATA]:
            item[PeriodicConstants.COMMUNITY_ID] = response.data[PeriodicConstants.COMMUNITY].id
            item[PeriodicConstants.COMMUNITY_NAME] = response.data[PeriodicConstants.COMMUNITY].name

        isValid, output = ResourceController.createProviderResource(_data[CommunityConstants.LEASING_DATA]
                                                                    , jwtToken, True)
        """
        # Testing Purpose
        _test = BaseResponse()
        _test.data = {
            "resourceData": [
                {
                    "name": "test",
                    "id": "24b9fdd2d404ff35cfd39887449ec64a",
                    "communityID": "24b9fdd2d404ff35cfd39887449eb30b",
                    "created": "2021-04-14 18:42:21"
                },
                {
                    "name": "second test",
                    "id": "24b9fdd2d404ff35cfd39887449edd54",
                    "communityID": "24b9fdd2d404ff35cfd39887449eb30b",
                    "created": "2021-04-14 18:42:21"
                }
            ]
        }
        _test.error = {}
        # Testing Purpose
        isValid, output = True, _test
        """
        if not isValid:
            return False, Convert.toJson(output)

        response.data[PeriodicConstants.RESOURCE] = output.data[CommunityConstants.LEASING_DATA]
        response.error.update(output.error)

        # Construct createBookable parameters.
        _data[CommunityConstants.BOOKABLE_DATA][PeriodicConstants.COMMUNITY_NAME] = \
            response.data[PeriodicConstants.COMMUNITY].name
        _data[CommunityConstants.BOOKABLE_DATA][PeriodicConstants.COMMUNITY_ID] = \
            response.data[PeriodicConstants.COMMUNITY].id
        _data[CommunityConstants.BOOKABLE_DATA]['senderEmail'] = \
            communityData[CommunityConstants.EMAIL]

        _resourceId = []
        for item in response.data[PeriodicConstants.RESOURCE]:
            _resourceId.append(item.id)

        _data[CommunityConstants.BOOKABLE_DATA][PeriodicConstants.RESOURCE_ID] = _resourceId

        bookableParam = {
            CommunityConstants.BOOKABLE_DATA: _data[CommunityConstants.BOOKABLE_DATA]
        }

        isValid, output = BookableController.createBookable(bookableParam, jwtToken, True)
        output = json.loads(output)
        if not isValid:
            return False, Convert.toJson(output)
        response.data[PeriodicConstants.BOOKABLE] = output[PeriodicConstants.DATA]
        return True, Convert.toJson(response)

    @staticmethod
    def getCommunity(_id: str, jwtToken: dict):
        _body, _header, _error = {}, {}, {}
        _body = Periodic.getProvider()
        _body.params.id = _id

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        return _body, _header, _error

    @staticmethod
    def updateCommunity(_data: dict, jwtToken: dict):
        _body, _header, _error = {}, {}, {}

        isValid, error = Validate.schema(Schema.UPDATE_COMMUNITY, _data)

        # Validate availability data
        if PeriodicConstants.AVAILABILITY in _data and ('start' not in error) and ('end' not in error):
            # Validate Community availability data
            isValidCommunityData, errorCommunityData = validateAvailability(
                _data[PeriodicConstants.AVAILABILITY], CommunityConstants.COMMUNITY_DATA)
            if not isValidCommunityData:
                isValid = False
                error.update(errorCommunityData)

        if not isValid:
            response = BaseResponse()
            response.error = error
            return {}, {}, response

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}

        # Required Fields
        _body = Convert.toDict(Periodic.updateProvider())
        _body[PeriodicConstants.PARAMS]['subdomain'] = _data[CommunityConstants.SUBDOMAIN]

        if PeriodicConstants.TIMEZONE in _data:
            _body[PeriodicConstants.PARAMS]['timezone'] = _data[PeriodicConstants.TIMEZONE]
        if PeriodicConstants.DESCRIPTION in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.DESCRIPTION] = _data[PeriodicConstants.DESCRIPTION]
        if CommunityConstants.FACEBOOK in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.FACEBOOK] = _data[CommunityConstants.FACEBOOK]
        if CommunityConstants.INSTAGRAM in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.INSTAGRAM] = _data[CommunityConstants.INSTAGRAM]
        if CommunityConstants.PINTREST in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.PINTREST] = _data[CommunityConstants.PINTREST]
        if CommunityConstants.WEBSITE in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.WEBSITE] = _data[CommunityConstants.WEBSITE]
        if CommunityConstants.INTERNAL_CODE in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.INTERNAL_CODE] = _data[CommunityConstants.INTERNAL_CODE]
        if CommunityConstants.EMAIL in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.EMAIL] = _data[CommunityConstants.EMAIL]
        if CommunityConstants.REPLY_EMAIL in _data:
            _body[PeriodicConstants.PARAMS][CommunityConstants.REPLY_EMAIL] = _data[CommunityConstants.REPLY_EMAIL]
        if PeriodicConstants.PHONE in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.PHONE] = _data[PeriodicConstants.PHONE]
        if PeriodicConstants.ADDRESS in _data:
            _body[PeriodicConstants.PARAMS][PeriodicConstants.ADDRESS] = _data[PeriodicConstants.ADDRESS][
                PeriodicConstants.STREET_ADDRESS]
            _body[PeriodicConstants.PARAMS][PeriodicConstants.CITY] = _data[PeriodicConstants.ADDRESS][
                PeriodicConstants.CITY]
            _body[PeriodicConstants.PARAMS][PeriodicConstants.STATE] = _data[PeriodicConstants.ADDRESS][
                PeriodicConstants.STATE]
            _body[PeriodicConstants.PARAMS][PeriodicConstants.COUNTRY] = _data[PeriodicConstants.ADDRESS][
                PeriodicConstants.COUNTRY]
            _body[PeriodicConstants.PARAMS]['zip'] = _data[PeriodicConstants.ADDRESS][PeriodicConstants.POSTAL_CODE]

        if PeriodicConstants.AVAILABILITY in _data:
            availability = {PeriodicConstants.FRIDAY: [], PeriodicConstants.MONDAY: [], PeriodicConstants.SATURDAY: [],
                            PeriodicConstants.SUNDAY: [], PeriodicConstants.THURSDAY: [], PeriodicConstants.TUESDAY: [],
                            PeriodicConstants.WEDNESDAY: []}
            if PeriodicConstants.FRIDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.FRIDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.FRIDAY])
            if PeriodicConstants.MONDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.MONDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.MONDAY])
            if PeriodicConstants.SATURDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.SATURDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.SUNDAY])
            if PeriodicConstants.THURSDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.THURSDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.THURSDAY])
            if PeriodicConstants.TUESDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.TUESDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.TUESDAY])
            if PeriodicConstants.WEDNESDAY in _data[PeriodicConstants.AVAILABILITY]:
                availability[PeriodicConstants.WEDNESDAY] = CommunityController.constructAvailabilityObj(
                    _data[PeriodicConstants.AVAILABILITY][PeriodicConstants.WEDNESDAY])
            _body[PeriodicConstants.PARAMS]['businesshours'] = availability
        return _body, _header, _error

    @staticmethod
    def deleteCommunity(_data: dict, jwtToken: dict):
        response = BaseResponse()

        # Get ResourceID using communityID
        _body, _header, _errorResponse = ResourceController.getResource(_data, jwtToken)
        res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
        # Format GetResource API response
        isValid, output = ResourceController.formatResourceResponse(res.status_code, json.loads(res.text),
                                                                    Schema.GET_RESOURCE)
        # ResourceID under Community
        resourceID = []
        for item in output.data:
            resourceID.append(item.id)
        # Construct DeleteProviderResource parameter
        resourceData = {PeriodicConstants.COMMUNITY_ID: _data[PeriodicConstants.COMMUNITY_ID],
                        PeriodicConstants.RESOURCE_ID: resourceID}
        _isValid, output = ResourceController.deleteProviderResource(resourceData, jwtToken)
        if not _isValid:
            return False, output
        else:
            response.data.update(output.data)

        # Get BookableID using communityID
        _body, _header, _errorResponse = BookableController.getBookable(_data, jwtToken)
        res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
        # Format GetBookable API response
        isValid, output = BookableController.formatBookableResponse(res.status_code, json.loads(res.text),
                                                                    Schema.GET_BOOKABLE)

        # BookableID under Community
        bookableID = output.data.id
        # Construct delete Bookable parameter
        bookableData = {PeriodicConstants.ID: bookableID}
        _body, _header, _errorResponse = BookableController.deleteBookable(bookableData, jwtToken)
        res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
        isValid, output = BookableController.formatBookableResponse(res.status_code, json.loads(res.text),
                                                                    Schema.DELETE_BOOKABLE)
        if not _isValid:
            return False, output
        else:
            response.data[CommunityConstants.BOOKABLE_DATA] = output.data

        _body, _header = {}, {}
        _body = Periodic.deleteProvider()
        _body.params.id = _data[PeriodicConstants.COMMUNITY_ID]

        _header = {PeriodicConstants.AUTHORIZATION: Periodic.token(jwtToken[PeriodicConstants.JWT_ISSUER],
                                                                   jwtToken[PeriodicConstants.JWT_SUBJECT],
                                                                   jwtToken[PeriodicConstants.JWT_KEY])}
        res = sendRequest(HTTPRequest.POST, Convert.toJson(_body), '', _header)
        isValid, output = CommunityController.formatCommunityResponse(res.status_code, json.loads(res.text),
                                                                      Schema.DELETE_COMMUNITY)
        if not _isValid:
            return False, output
        response.data[CommunityConstants.COMMUNITY_DATA] = output.data
        return True, response

    @staticmethod
    def constructAvailabilityObj(_data: list):
        res = []
        for item in _data:
            if len(item['start']) > 0 and len(item['end']) > 0:
                res.append({
                    "start": list(map(int, item['start'].split(':'))),
                    "end": list(map(int, item['end'].split(':')))
                })
        return res

    @staticmethod
    def convertAvailability(_data: dict):
        availability = {
            "monday": [],
            "friday": [],
            "saturday": [],
            "sunday": [],
            "thursday": [],
            "tuesday": [],
            "wednesday": []
        }
        for item in _data.keys():
            if len(_data[item]) > 0:
                for _availabilityObj in _data[item]:
                    availability[item].append({
                        'start': str((datetime.datetime.strptime(
                            str(_availabilityObj['start'][0]) + ":" + str(
                                _availabilityObj['start'][1]) + ":" + str(_availabilityObj['start'][2]),
                            "%H:%M:%S"))).split(' ')[1],
                        'end': str((datetime.datetime.strptime(
                            str(_availabilityObj['end'][0]) + ":" + str(
                                _availabilityObj['end'][1]) + ":" + str(_availabilityObj['end'][2]),
                            "%H:%M:%S"))).split(' ')[1]
                    })
        return availability

    @staticmethod
    def formatCommunityResponse(responseCode, responseData: dict, _type: Schema):
        response = BaseResponse()
        if responseCode == 200:
            if _type == Schema.DELETE_COMMUNITY:
                response.data = {PeriodicConstants.ID: responseData[PeriodicConstants.RESULT][PeriodicConstants.ID],
                                 PeriodicConstants.MESSAGE: "community deleted."}
            else:
                community = Community()
                community.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
                community.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
                community.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
                community.internalCode = responseData[PeriodicConstants.RESULT][PeriodicConstants.INTERNAL_CODE]
                community.subDomain = responseData[PeriodicConstants.RESULT]['subdomain']
                community.phone = responseData[PeriodicConstants.RESULT][PeriodicConstants.PHONE]
                community.email = responseData[PeriodicConstants.RESULT][PeriodicConstants.EMAIL]
                community.replyEmail = responseData[PeriodicConstants.RESULT]['replyto']
                community.website = responseData[PeriodicConstants.RESULT][PeriodicConstants.URL]
                community.facebookURL = responseData[PeriodicConstants.RESULT]['facebook']
                community.twitterURL = responseData[PeriodicConstants.RESULT]['twitter']
                community.instagramURL = responseData[PeriodicConstants.RESULT]['instagram']
                community.pinterestURL = responseData[PeriodicConstants.RESULT]['pinterest']
                community.timezone = responseData[PeriodicConstants.RESULT][PeriodicConstants.TIMEZONE]
                community.description = responseData[PeriodicConstants.RESULT][PeriodicConstants.DESCRIPTION]
                community.address = responseData[PeriodicConstants.RESULT][PeriodicConstants.ADDRESS]
                community.state = responseData[PeriodicConstants.RESULT][PeriodicConstants.STATE]
                community.country = responseData[PeriodicConstants.RESULT][PeriodicConstants.COUNTRY]
                community.postalCode = responseData[PeriodicConstants.RESULT]['zip']
                community.availability = CommunityController.convertAvailability(
                    responseData[PeriodicConstants.RESULT]['businesshours'])
                response.data = community
            return True, response
        if responseCode == 201:
            # Constructing Community Part of the Response
            community = Community()
            community.name = responseData[PeriodicConstants.RESULT][PeriodicConstants.NAME]
            community.id = responseData[PeriodicConstants.RESULT][PeriodicConstants.ID]
            community.modified = responseData[PeriodicConstants.RESULT][PeriodicConstants.MODIFIED]
            community.internalCode = responseData[PeriodicConstants.RESULT][PeriodicConstants.INTERNAL_CODE]
            community.subDomain = responseData[PeriodicConstants.RESULT]['subdomain']
            community.phone = responseData[PeriodicConstants.RESULT][PeriodicConstants.PHONE]
            community.email = responseData[PeriodicConstants.RESULT][PeriodicConstants.EMAIL]
            community.replyEmail = responseData[PeriodicConstants.RESULT]['replyto']
            community.website = responseData[PeriodicConstants.RESULT][PeriodicConstants.URL]
            community.facebookURL = responseData[PeriodicConstants.RESULT]['facebook']
            community.twitterURL = responseData[PeriodicConstants.RESULT]['twitter']
            community.instagramURL = responseData[PeriodicConstants.RESULT]['instagram']
            community.pinterestURL = responseData[PeriodicConstants.RESULT]['pinterest']
            community.timezone = responseData[PeriodicConstants.RESULT][PeriodicConstants.TIMEZONE]
            community.description = responseData[PeriodicConstants.RESULT][PeriodicConstants.DESCRIPTION]
            community.address = responseData[PeriodicConstants.RESULT][PeriodicConstants.ADDRESS]
            community.state = responseData[PeriodicConstants.RESULT][PeriodicConstants.STATE]
            community.country = responseData[PeriodicConstants.RESULT][PeriodicConstants.COUNTRY]
            community.postalCode = responseData[PeriodicConstants.RESULT]['zip']
            community.availability = CommunityController.convertAvailability(
                responseData[PeriodicConstants.RESULT]['businesshours'])
            response.data = community
            return True, response
        elif responseCode == 409:
            response.error = {
                CommunityConstants.COMMUNITY_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 401:
            response.error = {CommunityConstants.COMMUNITY_DATA: ''.join(
                responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE].split(
                    PeriodicConstants.PERIODIC_ERROR))}
            return False, response
        elif responseCode == 404:
            if "provider not found" in responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]:
                response.error = {CommunityConstants.COMMUNITY_DATA: "community not found"}
            else:
                response.error = {
                    CommunityConstants.COMMUNITY_DATA: responseData[PeriodicConstants.ERROR][PeriodicConstants.MESSAGE]}
            return False, response
        elif responseCode == 500:
            response.error = {
                PeriodicConstants.PLATFORM_DATA: ''.join(
                    responseData[PeriodicConstants.ERROR][PeriodicConstants.DATA])}
            return False, response
        else:
            response.error = {
                PeriodicConstants.PLATFORM_DATA: responseData}
            return False, response

from enum import Enum
import logging
from DataPushPullShared.Utilities.DataController import QuextIntegrationConstants
from VendorShared.Model.ServiceRequest import ServiceRequest


class ApiSchema(Enum):
    LOCATION = 0
    RESIDENT = 1
    LEASING = 2
    UNIT_AVAILABILITY = 3
    TOUR_SCHEDULE = 4
    GUEST_CARD = 5    
    TOUR_AVAILABILITY = 6

api_headers = {
    ApiSchema.LOCATION: {
        "HTTP_CUSTOMERUUID": 'customerUUID',
        "HTTP_COMMUNITYUUID": 'communityUUID',
        "HTTP_X_API_KEY": 'apiKey'
    },
    ApiSchema.RESIDENT: {
        "HTTP_CUSTOMERUUID": 'customerUUID',
        "HTTP_COMMUNITYUUID": 'communityUUID',
        "HTTP_X_API_KEY": 'apiKey'
    },
    ApiSchema.LEASING: {
        "HTTP_CUSTOMERUUID": 'customerUUID',
        "HTTP_COMMUNITYUUID": 'communityUUID',
        "HTTP_X_API_KEY": 'apiKey'
    },
    ApiSchema.TOUR_SCHEDULE: {
        "HTTP_CUSTOMERUUID": 'customerUUID',
        "HTTP_COMMUNITYUUID": 'communityUUID',
        "HTTP_X_API_KEY": 'apiKey'
    },
    ApiSchema.GUEST_CARD: {
        "HTTP_AUTHORIZATION": 'apiKey'
    },
    ApiSchema.UNIT_AVAILABILITY: {
        "HTTP_AUTHORIZATION": 'apiKey'
    },
    ApiSchema.TOUR_AVAILABILITY: {
        "HTTP_AUTHORIZATION": 'apiKey'
    }
}


def build_params(payload=None, endpoint: ApiSchema = None):
    """ build params will build the parameters
        with the payload dict object based on
        the endpoint type"""
    return {api_headers[endpoint][i]: j.strip("Bearer ") for i, j in payload.items() if i in api_headers[endpoint].keys()}


def build_optional_params(input, service_request:ServiceRequest):
    page_no = hasattr(input, QuextIntegrationConstants.PAGE) and input.page or 1
    createdAfter = hasattr(input, QuextIntegrationConstants.CREATED_AFTER) and input.createdAfter or None
    updatedAfter = hasattr(input, QuextIntegrationConstants.UPDATED_AFTER) and input.updatedAfter or None
    createdBefore = hasattr(input, QuextIntegrationConstants.CREATED_BEFORE) and input.createdBefore or None
    updatedBefore = hasattr(input, QuextIntegrationConstants.UPDATED_BEFORE) and input.updatedBefore or None
    service_request.page = int(page_no)
    service_request.created_after = createdAfter
    service_request.updated_after = updatedAfter
    service_request.created_before = createdBefore
    service_request.updated_before = updatedBefore


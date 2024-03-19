import os

class Constants:
    PATH = '/api/conservice'
    HOST = os.environ.get("MADERA_HOST")
    HTTP_BAD_RESPONSE_CODE = 400
    HTTP_GOOD_RESPONSE_CODE = 200
    OUTGOING_CONNECTION_NAME = 'Conservice_Outgoing_Channel'
    GET_CHARGE_CODES = 'get-charge-codes'
    GET_PROPERTIES = 'get-properties'
    POST_ADD_CHARGES = 'add-charges' 
    INVALID_PARAMETER = 'Invalid Parameter'
    INVALID_PROPERTY = 'Invalid Property'
    MISSING_CHARGES = 'missing charges'
    PROPERTIES = 'properties'
    METHODS = 'methods'
    CHARGES = 'charges'
    PARAMETER = 'Parameter'
    START_DATE = 'start_date'
    END_DATE = 'end_date'
    TENANTS = 'tenants'
    LEASES = 'leases'
    CHARGES = 'charges'
    BODY = 'body'
    RESIDENT_STATUS = 'resident-status'
    CURRENT = "current"


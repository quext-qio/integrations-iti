class EntrataConstants:
    GET_CURRENT_LEASES_CHANNEL = "Entrata_Get_Leases"
    PROPERTY_CALENDAR_AVAILABILITY = "propertyCalendarAvailability"
    GET_LOCATION_CHANNEL = "Entrata_Locations_Channel"
    CALENDAR_EVENT_CATEGORY_IDS = "calendarEventCategoryIds"
    GET_CALENDAR_AVAILABILITY = "getCalendarAvailability"
    SUCCESS = "success"
    RESPONSE = "response"
    RESULT = "result"
    CUSTOMERS = "Customers"
    CUSTOMER = "Customer"
    ATTRIBUTES = "@attributes"
    ID = "Id"
    GETCUSTOMERS = "getCustomers"
    GETLEADS = "getLeadPickLists"
    GETLEASES = "getLeases"
    GETPROPERTYUNITS = "getPropertyUnits"
    GETUNITANDPRICING = "getUnitsAvailabilityAndPricing"
    GETPROPERTIES = "getProperties"    
    GETLOCATIONS = "getPropertyUnits"
    LEADS = "leads"
    PROPERTIES = "properties"
    SENDLEADS = "sendLeads"
    PROPERTYID = "propertyId"
    PROPERTYIDS = "propertyIds"
    MARKETINGNAME = "MarketingName"
    PHYSICALPROPERTY = "PhysicalProperty"
    IDENTIFICATION = "Identification"
    IDVALUE = "IDValue"
    NAME = "Name"
    COUNT = "Count"
    ROOM = "Room"
    UNITCOUNT = "UnitCount"
    UNITSAVAILABLE = "UnitsAvailable"
    MARKETRENT = "MarketRent"
    SQUAREFEET = "SquareFeet"
    MIN = "Min"
    MAX = "Max"
    COMMENT = "Comment"
    ADDRESS = "Address"
    CITY = "City"
    STATE = "State"
    POSTALCODE = "PostalCode"
    EMAILL = "Email"
    AVAILABILITY = "Availability"
    NOTAVAILABLE = "Not Available"
    AVAILABLEON = "AvailableOn"
    FLOORPLANNAME = "FloorPlanName"
    BUILDINGNAME = "BuildingName"
    PROPERTYUNITID = "PropertyUnitId"
    UNITNUMBER = "UnitNumber"
    FLOORPLANID = "FloorplanId"
    RENT = "Rent"
    MINRENT = "MinRent"
    ILS_UNITS = "ILS_Units"
    MODELS_DICT = 'models_dict'
    PROP_DICT = 'prop_dict'
    AVAILABLE = "Available"
    FILTER_ON_AVAILABILITY = "filter_on_availability"
    FLOORPLANS = "Floorplans"
    FLOORPLAN = "Floorplan"
    BEDROOM = "Bedroom"
    BATHROOM = "Bathroom"
    FORIEGNCOMMUNITYID = 'foreign_community_id'
    PROPERTY = 'property'
    PROPERTIES = 'properties'
    URLCUSTOMERPARAMETER = "customers"
    URLPROPERTYPARAMETER = "propertyunits"
    URLLEASEPARAMETER = "v1/leases"
    UNITS = 'units'
    UNIT = 'unit'
    LEASES = "leases"
    ENTRATA_CHANNEL_NAME = 'Entrata (External)'
    APPLICANT = "applicant"
    APPLICANTS = "applicants"
    ATTRIBUTES = "@attributes"
    FIRSTNAME = "firstName"
    LASTNAME = "lastName"
    PROSPECTS = "prospects"
    PROSPECT = "prospect"
    STATUS = "status"
    APPLICANTID = "applicantId"
    MESSAGE = "message"
    INCLEASEHISTORY = "includeLeaseHistory"
    CANCELLED = "Cancelled"
    FROM_DATE = "fromDate"
    TO_DATE = "toDate"
    QUEXT_DATE_FORMAT = '%Y-%m-%d'
    ENTRATA_DATE_FORMAT = '%m/%d/%Y'
    ENTRATA_QUEXT_LEAD_SOURCE_ID = 'ENTRATA_QUEXT_LEAD_SOURCE_ID'
    ENTRATA_REASON_ID = 'ENTRATA_REASON_ID'
    ENTRATA_AGENT_ID = "ENTRATA_AGENT_ID"
    PHONENUMBER = 'phoneNumber'
    PHONE = 'phone'
    EVENT_TYPE = "eventtype"
    EVENT_DATE = "eventdate"
    FIRST_NAME = "first_Name"
    LAST_NAME = "last_Name"
    EMAIL = "email"
    EVENT_UNITSAPCE_ID = 'eventunitspaceID'
    BOOK_TOUR_EVENT = 'SelfGuidedTour'
    PROSPECTS = "prospects"
    PROSPECT = "prospect"
    REQUEST_ID = "requestId"
    AVAILABLE_HOURS = "availableHours"
    AVAILABLE_HOUR = "availableHour"
    DATE = "date"
    START_TIME = "startTime"
    END_TIME = "endTime"
    DATETIME_FORMAT = '%m/%d/%Y %H:%M:%S'
    EVENTS = 'events'
    EVENT = 'event'
    ENTRATA_TIMEZONE = 'MST'
    QUEXT_TIMEZONE = 'GMT'
    GUESTCARD_METHOD = 'Online Guest Card'
    GUESTCARD_ID = 10
    WEBVISIBLE = 'WebVisible'
    MAKE_READY_DATE= 'MakeReadyDate'
    APPLICATION_ID = "applicationId"  

class ResponseSchema:
    """ Response Schema for Different Entrata Endpoints"""
    CUSTOMERS_RESPONSE_FORMAT = {
        'Customers': {
            'type': 'dict',
            'schema': {
                'Customer': {'type': 'list', 'required': True, 'minlength': 1}
            }
        }
    }

    LOCATION_RESPONSE_FORMAT = {
        'properties': {
            'type': 'dict',
            'schema': {
                'property': {'type': 'list', 'required': True, 'minlength': 1}
            }
        }
    }

    LEASES_RESPONSE_FORMAT = {
        'currencyCode': {'type': 'string'},
        'leases': {
            'type': 'dict',
            'schema': {
                'lease': {'type': 'list', 'required': True, 'minlength': 1}
            }
        }
    }

    GUESTCARD_RESPONSE_FORMAT = {
        "response": {
            "type": "dict",
            "schema": {
                "requestId": {"type": "string"},
                "code": {"type": "integer"},
                "result": {
                    "type": "dict",
                    "schema": {
                        "prospects": {
                            "type": "dict",
                            "schema": {
                                "prospect": {
                                    "type": "list"},
                                "schema": {
                                    "type": "dict",
                                    "schema": {
                                        "node": {"type": "integer"},
                                        "applicationId": {"type": "integer"},
                                        "applicantId": {"type": "integer"},
                                        "status": {"type": "integer"},
                                        "message": {"type": "string"},
                                        "applicants": {"type": "dict"},
                                        "applicant": {
                                            "type": "list",
                                            "schema": {
                                                "type": "dict",
                                                "schema": {
                                                    "id": {"type": "integer"},
                                                    "applicationId": {"type": "integer"},
                                                    "applicantId": {"type": "integer"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    BOOK_TOUR_RESPONSE_FORMAT = {
        'prospects': {
            'type': 'dict',
            'schema': {
                'prospect': {'type': 'list', 'required': True, 'minlength': 1}
            }
        }
    }

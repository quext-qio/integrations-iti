from enum import Enum
import logging


class VendorConstants:
    """
    Vendor Constants
    """
    COMMUNITY_UUID = 'communityUUID'
    CUSTOMER_UUID = 'customerUUID'
    PROPERTY_UUID = 'propertyUUID'
    PARTNER_ID = 'partnerUUID'
    PURPOSE = 'purpose'
    PARAMS = 'params'
    GET_PLATFORM_OUTGOING_CHANNEL = 'Integrated Partner Storage [Purposes] (Internal)'
    GET_PARTNER_OUTGOING_CHANNEL = 'Integrated Partners (Internal)'
    GET_SECURITY_OUTGOING_CHANNEL = 'Integrated Partner Storage [ACLs] (Internal)'
    PLATFORM_DATA = 'platformData'
    PLATFORM = 'platform'
    INVALID_DATA = 'Invalid Platform Data'
    BAD_REQUEST = 400
    CONFLICT = 409
    INVALID_DATE_FORMAT = 'Invalid Date Value'
    SUCCESS = 'Success'
    FAILED = 'Failed'
    STATUS = 'Status'
    RESMAN = 'ResMan'
    NAME = 'name'
    CONTENT = 'content'
    UUID = 'uuid'
    SECURITY = 'security'
    BODY = 'body'
    CREDENTIALS = 'credentials'
    RESIDENTS: str = "residents"
    UNIT = 'UNIT'
    UNITS = 'units'
    VENDOR_INFO_CACHE = 'Vendor_Info_cache'
    BUILTIN = 'builtin'
    INVALID_SECURITY = "Invalid Security Conifguration"
    LEASEMANAGEMENT = "leaseManagement"
    METHOD = "method"
    MDM_DB = "MDM DB"
    US = "US"
    UNIT_AVAILABILITY = "unitAvailability"
    TOUR_AVAILABILITY = "tourAvailability"
    TOUR_SCHEDULE = "scheduleTour"
    GET_CALENDAR_AVAILABILITY_OUTGOING_CHANNEL = "[Quext Calendar] Availability Times"
    QUEXT_SCHEDULE_TOUR = '[Quext Calendar] Schedule Tour'
    QUEXT_GET_AVAILABILITY = '[Quext Calendar] Availability Times'
    GUEST_CARD = "guestCards"
    PROPERTY_ID = "propertyId"
    ORIGINATING_LEAD_SOURCE_ID = "originatingLeadSourceId"
    CREATED_DATE = "createdDate"
    FIRST_NAME = "firstName"
    LAST_NAME = "lastName"
    PERSONAL_PHONE_NUMBER = "personalPhoneNumber"
    EMAIL = "email"
    EVENT_TYPE_ID = "eventtypeId"
    EVENT_TYPE = "eventtype"
    EVENT_DATE = "eventdate"
    EVENT_DATE_TIME = "eventdateTime"
    EVENT_REASON = "eventReason"
    ADD = "add"
    MOD = "mod"
    CURRENT = "Current"
    NOTICE = "Notice"
    PENDING = "Pending"
    PENDINGT = "Pending Transfer"
    EVICTED = "Evicted"
    PAST = "Past"
    ACTIVE = "Active"
    QUEUED = "Queued"
    TERMINATED = "Terminated"
    ARCHIVED = "Archived"
    FUTURE = "Future"
    INVALID_SOURCE = 'Invalid source system'
    PROSPECT = "guest"
    FIRSTNAME = "first_name"
    LASTNAME = "last_name"
    PHONE = "phone"
    COMMENT = "guestComment"
    TOUR_SCHEDULE_DATA = "tourScheduleData"
    START = "start"
    SOURCE = "source"
    CUSTOMER_PREFERENCE = "guestPreference"
    DESIRED_BEDROOM = "desiredBeds"
    DESIRED_RENT = "desiredRent"
    DESIRED_BATHROOM = "desiredBaths"
    MOVE_IN_DATE = "moveInDate"
    CONTACT_PREFERENCE = "contactPreference"
    LEASE_TERM_MONTHS = "leaseTermMonths"
    NO_OF_OCCUPANTS = "noOfOccupants"
    MOVE_IN_REASON = "moveInReason"
    PREFERRED_AMENITIES = "preferredAmenities"
    MOVEIN_FORMAT = '%Y-%m-%d'
    SOURCE_SYSTEM = {'Quext Websites': 'WS',
                     'Quext Digital Human': 'DH'
                     }
    APIKEY = "apiKey"
    PARTNER_NAME = "partner_name"
    DH = "dh"
    WS = "ws"
    DHWSDL=""
    AGENT_ID = "agentId"
    TOUR_INFORMATION = "tourInformation"
    INSERT = "INSERT"
    NEW = "NEW"
    UPDATE = "UPDATE"
    EXIST = 'EXIST'
    RESMAN_DATE_FORMAT = "%Y-%m-%d"
    ENTRATA_DATE_FORMAT = "%m/%d/%Y"
    NEWCO_DATE_FORMAT = "%Y-%m-%d"
    REALPAGE_DATE_FORMAT = "%m/%d/%Y"
    IPS_DB = "IPS_DB"


class PartnerConditionConstants:
    """
    Partner Condition Constants
    """
    # 'Rented','Model','Down','Vacant - Not Leased','Vacant - Leased',
    # 'NTV - Available','NTV - Leased','Inactive','Shop','Rehab','Pending Approval'
    RESMAN = ["residential"]
    NEWCO = ["Pending Approval", "Down", "Demo", "Inactive", "Rehab", "Office"]
    ENTRATA = ["1"]
    REALPAGE = ["true"]


class PartnerConstants:
    """
    Partner Constants
    """
    ENTRATA = "Entrata"
    RESMAN = "ResMan"
    NEWCO = "Newco"
    REALPAGE = "RealPage"
    FUNNEL = "Funnel"


class VendorLayout(Enum):
    ENTRATA = 0
    REALPAGE = 1
    FUNNEL = 2
    RESMAN = 3


layout_details = {
    VendorLayout.ENTRATA: {
        "ONE_BEDROOM": '1',
        "TWO_BEDROOM": '2',
        "THREE_BEDROOM": '3'
    },
    VendorLayout.REALPAGE: {
        "ONE_BEDROOM": '1',
        "TWO_BEDROOM": '2',
        "THREE_BEDROOM": '3'
    },
    VendorLayout.FUNNEL: {
        "ONE_BEDROOM": '1br',
        "TWO_BEDROOM": '2br',
        "THREE_BEDROOM": '3br',
        "FOUR_BEDROOM": '4+br',
        "STUDIO": 'studio',
        "LOFT": 'loft'
    },
    VendorLayout.RESMAN: {
        "ONE_BEDROOM": '1',
        "TWO_BEDROOM": '2',
        "THREE_BEDROOM": '3'
    }
}


class SourceLayout(Enum):
    DH = "Digital Human"
    WS = "website"


def get_vendor_layout(source, payload):
    source_list_items = [layout_details[source][item] for item in payload if layout_details[source].get(item)]
    return source_list_items


def get_source_and_agent(source: str, service_request):
    logging.info("Finding source for Guest card")
    agent_id = ""
    if not source:
        logging.info("Invalid Source received")
        return "", agent_id
    source = source.upper()
    source_name = SourceLayout.DH.value \
        if SourceLayout.DH.name == source else SourceLayout.WS.value if SourceLayout.WS.name == source else None
    if service_request.auth.get_property(source):
        source_details = service_request.auth.get_property(source)
        agent_id = source_details[VendorConstants.AGENT_ID]
    logging.debug("Source = {}, AgentId = {}".format(source, agent_id))
    return source_name, agent_id

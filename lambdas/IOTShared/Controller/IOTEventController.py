from datetime import datetime

from DataPushPullShared.Utilities.Entities import Person, Resident, Lease, LeaseInterval, Unit
from IOTShared.Model.IOTEventMessageModel import ResidentMessage, LocationMessage, LeaseMessage, ApartmentMessage, UnitspaceMessage
from MessageBusShared.Utilities.MessageBusUtils import MessageBusUtils
from VendorShared.Model.ServiceRequest import ServiceRequest
from VendorShared.Utilities.Utils import min_start_date, max_end_date, lease_status_mapping
from VendorShared.Utilities.VendorConstants import VendorConstants


class IOTEventController:
    """
    IOTEvent Controller responsible for posting events to Kafka only specific to IOT product
    """

    def __init__(self, service_request: ServiceRequest):
        self.service_request = service_request
        self.messagebus_utils = MessageBusUtils()

    def send_resident_event(self, person: Person, resident: Resident, event_action: str):
        """
        Send Resident event to IOT kafka message bus

        @param event_action: Event action tells the add or mod action happens
        @param person: Person object used to construct IOT Resident Object
        @param resident: Resident object used to construct IOT Resident Object
        """
        resident_message = ResidentMessage()
        resident_message.eventDate = self.__event_time()
        resident_message.eventType = IOTEventConstants.delimiter.join([IOTEventConstants.RESIDENT, event_action])
        resident_message.communityId = person.community_id
        resident_message.personId = resident.person_id
        resident_message.externalId = resident.external_id
        resident_message.firstName = person.first_name
        resident_message.lastName = person.last_name
        self.messagebus_utils.send_iot_event(self.service_request.definition, payload=resident_message)

    def send_location_event(self, unit: Unit, event_action: str, unitspace_obj=[]):
        """
        Send Location event to IOT kafka message bus

        @param unit: Unit object used to construct IOT Location Object
        @param event_action: Event action tells the add or mod action happens
        """
        if event_action:
            building = LocationMessage()
            building.eventDate = self.__event_time()
            building.eventType = IOTEventConstants.delimiter.join([IOTEventConstants.LOCATION, event_action])
            building.communityId = unit.community_id
            building.externalId = "{}-{}".format(unit.community_id, unit.building)
            building.name = unit.unit_name
            building.type = IOTEventConstants.BUILDING
            self.messagebus_utils.send_iot_event(self.service_request.definition, payload=building)

            apartment = ApartmentMessage()
            apartment.eventDate = self.__event_time()
            apartment.eventType = IOTEventConstants.delimiter.join([IOTEventConstants.LOCATION, event_action])
            apartment.communityId = unit.community_id
            apartment.externalId = unit.external_id
            apartment.locationId = unit.unit_id
            apartment.name = unit.unit_name
            apartment.type = IOTEventConstants.APARTMENT
            apartment.businessPurpose = IOTEventConstants.UNIT
            apartment.parentIdExternal = building.externalId
            self.messagebus_utils.send_iot_event(self.service_request.definition, payload=apartment)

        for unit_space in unitspace_obj:
            event_action = None
            if hasattr(unit_space, 'is_insert'):
                event_action = VendorConstants.ADD
            elif hasattr(unit_space, 'is_update'):
                event_action = VendorConstants.MOD
            if event_action:
                unitspace = UnitspaceMessage()
                unitspace.eventDate = self.__event_time()
                unitspace.eventType = IOTEventConstants.delimiter.join([IOTEventConstants.LOCATION, event_action])
                unitspace.communityId = unit.community_id
                unitspace.externalId = unit_space.external_id
                unitspace.unitspaceId = unit_space.unitspace_id
                unitspace.name = unit.unit_name
                unitspace.type = IOTEventConstants.UNITSAPCE
                unitspace.businessPurpose = IOTEventConstants.UNITSAPCE
                unitspace.parentIdExternal = unit.external_id
                self.messagebus_utils.send_iot_event(self.service_request.definition, payload=unitspace)

    def send_lease_event(self, lease: Lease, lease_intervals: list, event_action: str):
        """
        Send Lease event to IOT kafka message bus

        @param lease: Lease object used to construct IOT lease Object
        @param lease_intervals: List of LeaseInterval objects used to construct IOT lease Object
        @param event_action: Event action tells the add or mod action happens
        """
        lease_message = LeaseMessage()
        lease_message.eventDate = self.__event_time()
        lease_message.eventType = IOTEventConstants.delimiter.join([IOTEventConstants.LEASE, event_action])
        lease_message.communityId = lease.community_id
        lease_message.externalId = lease.external_id
        lease_message.leaseId = lease.lease_id
        lease_message.personId = lease.person_id
        lease_message.personIdExternal = lease.external_id
        lease_message.locationId = lease.unit_id
        lease_message.locationIdExternal = lease.external_id
        lease_message.startDate = min_start_date(lease_intervals)
        value = max_end_date(lease_intervals)
        lease_message.endDate = value and value[0] or None
        lease_message.moveInDate = lease.move_in_date
        lease_message.moveOutDate = value and value[0] or None
        if not lease.move_in_date:
            lease_message.status = VendorConstants.PENDING
        else:
            lease_message.status = lease_status_mapping(value and value[1] or None)
        self.messagebus_utils.send_iot_event(self.service_request.definition, payload=lease_message)

    def __event_time(self) -> str:
        return datetime.now().strftime(IOTEventConstants.ISO_DATE_FORMAT_8601)[:-3]


class IOTEventConstants:
    RESIDENT = "resident"
    LOCATION = "location"
    LEASE = "lease"
    BUILDING = "building"
    APARTMENT = "apartment"
    UNITSAPCE = "unit_space"
    UNIT = "unit"
    ISO_DATE_FORMAT_8601 = "%Y-%m-%d %H:%M:%S.%f"
    delimiter = "."

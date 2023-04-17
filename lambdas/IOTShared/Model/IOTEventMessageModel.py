from pydantic import BaseModel


class ResidentMessage(BaseModel):
    communityId: str = None
    eventDate: str = None
    eventType: str = None
    externalId: str = None
    personId: str = None
    firstName: str = None
    lastName: str = None


class LeaseMessage(BaseModel):
    communityId: str = None
    eventDate: str = None
    eventType: str = None
    externalId: str = None
    leaseId: str = None
    personId: str = None
    personIdExternal: str = None
    locationId: str = None
    locationIdExternal: str = None
    startDate: str = None
    endDate: str = None
    moveInDate: str = None
    moveOutDate: str = None
    status: str = None


class LocationMessage(BaseModel):
    communityId: str = None
    eventDate: str = None
    eventType: str = None
    externalId: str = None
    name: str = None
    type: str = None

class ApartmentMessage(LocationMessage):
    locationId: str = None
    businessPurpose: str = None
    parentIdExternal: str = None

class UnitspaceMessage(LocationMessage):
    unitspaceId: str = None
    businessPurpose: str = None
    parentIdExternal: str = None


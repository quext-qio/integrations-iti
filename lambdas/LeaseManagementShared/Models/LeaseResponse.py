from pydantic import BaseModel

class Lease:
    """
    Response model for zato endpoint
    """
    communityId : str
    leaseId : str
    externalId : str
    createdAt : str
    updatedAt : str
    personId : str
    personIdExternal : str
    locationId : str
    locationIdExternal : str
    startDate :str
    endDate : str
    moveInDate : str
    moveOutDate : str
    status : str

    def __init__(self,communityId="", externalId = "",personIdExternal = "", locationIdExternal= "" ,startDate="", endDate="", moveInDate="", moveOutDate="", status="", leaseId="", createdAt="", updatedAt="", personId="", locationId=""):
        self.communityId = communityId
        self.externalId = externalId
        self.personIdExternal = personIdExternal
        self.startDate = startDate
        self.endDate = endDate
        self.moveInDate = moveInDate
        self.moveOutDate = moveOutDate
        self.status = status
        self.leaseId = leaseId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.personId = personId
        self.locationId = locationId
        self.locationIdExternal = locationIdExternal


class Count(BaseModel):
    insert: int = 0
    update: int = 0

class LeaseImportResponse(BaseModel):
    lease:Count = Count()
    lease_interval:Count = Count()
    retable_items:Count = Count()
    locations:Count = Count()
    resident:Count = Count()
    person:Count = Count()
    address:Count = Count()
    unitspace:Count = Count()


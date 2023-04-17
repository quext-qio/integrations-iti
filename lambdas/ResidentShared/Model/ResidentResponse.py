from pydantic import BaseModel

class Resident:
    communityId: str = None
    personId: str = None
    externalId: str = None
    createdAt: str = None
    updatedAt: str = None
    firstName: str = None
    lastName: str = None
    email: str = None
    phone: str = None

    def __init__(self, communityId, externalId, firstName, lastName, email, phone):
        self.communityId, self.firstName, self.lastName, self.email, self.phone = communityId, firstName, lastName, email, phone
        self.externalId = externalId
        self.personId = None
        self.updatedAt = None
        self.createdAt = None


class Count(BaseModel):
    insert: int = 0
    update: int = 0

class ResidentImportResponse(BaseModel):
    resident:Count = Count()
    person:Count = Count()
    address:Count = Count()

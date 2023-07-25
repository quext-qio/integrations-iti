from pydantic import BaseModel

class Building:
    """
       Response model for Building Json
    """
    communityId: str = ""
    externalId: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    name: str = ""
    type: str = "building"

    def __init__(self, communityId, externalId, createdAt:str="", updatedAt:str="", name: str="", type:str = "building"):
        self.communityId = communityId
        self.externalId = externalId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.name = name
        self.type = type

class Units:
    """
    Response model for Units Json
    """
    communityId: str = ""
    externalId: str = ""
    locationId: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    name: str = ""
    type: str = ""
    businessPurpose:str = ""
    parentIdExternal:str = ""

    def __init__(self, communityId, externalId, locationId:str="", createdAt:str="", updatedAt:str="", name:str="", type:str = "apartment", businessPurpose:str= "unit", parentIdExternal:str=""):
        self.communityId = communityId
        self.externalId = externalId
        self.locationId = locationId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.name = name
        self.type = type
        self.businessPurpose = businessPurpose
        self.parentIdExternal = parentIdExternal

class UnitRoom:
    """
    Response model for Units Json
    """
    communityId: str = ""
    externalId: str = ""
    unitspaceId: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    name: str = ""
    type: str = ""
    businessPurpose:str = ""
    parentIdExternal:str = ""

    def __init__(self, communityId, externalId, unitspaceId:str="", createdAt:str="", updatedAt:str="", name:str="", type:str = "unitspace", businessPurpose:str= "unitspace", parentIdExternal:str=""):
        self.communityId = communityId
        self.externalId = externalId
        self.unitspaceId = unitspaceId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.name = name
        self.type = type
        self.businessPurpose = businessPurpose
        self.parentIdExternal = parentIdExternal

class Location(BaseModel):
    """
    Response model for Resman Endpoint
    
    """
    PropertyID: str = ""
    UnitId: str =""
    UnitNumber: str = ""
    Building: str = ""
    Floor: str = ""
    StreetAddress: str = ""
    City: str = ""
    State: str = ""
    Zip: str = ""
    UnitType: str = ""

class Count(BaseModel):
    insert: int = 0
    update: int = 0

class LocationImportResponse(BaseModel):
    locations:Count = Count()
    unitspace:Count = Count()
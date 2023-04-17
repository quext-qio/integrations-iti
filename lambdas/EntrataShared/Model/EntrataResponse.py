from pydantic import BaseModel
from typing import List, Optional


class Resident(BaseModel):
    """
    Response model for Entrata Endpoint
    """
    LeaseId: dict = ""
    attributes: dict = ""
    FirstName: str = ""
    LastName: str = ""
    UnitNumber: str = ""
    BuildingName: str = ""
    Address: str = ""
    City: str = ""
    State: str = ""
    PostalCode: str = ""
    Email: str = ""
    additionalEmail: str = ""
    PhoneNumber: str = ""

class UnitAddress(BaseModel):
    """
    Response model for Entrata Endpoint
    """
    address: str = ""
    city: str = ""
    state: str = ""
    postalCode: str = ""
    country: str = ""

class UnitSpaceItem(BaseModel):
    unitSpaceId: int = ""
    unitNumber: str = ""
    isAffordable: int = ""
    hasPricing: int = ""
    spaceConfiguration: str = None
    rent: dict = ""
    minDeposit: str = ""
    maxDeposit: str = ""
    occupancyTypeId: int = ""
    occupancyTypeName: str = ""
    exclusionReason: str = ""
    availabilityStatus: str = ""
    availableDate: str = ""
    unitAvailabilityURL: str = ""

class UnitSpaces(BaseModel):
    unitSpace: List[UnitSpaceItem]

class Location(BaseModel):
    """
    Response model for Entrata Endpoint
    """
    id: str =""
    unitTypeId: str = ""
    unitTypeName: str = ""
    unitNumber: str = ""
    buildingId: str = ""
    buildingName: str = ""
    floorplanId: str = ""
    numberOfBedrooms: int = ""
    numberOfBathrooms: int = ""
    maxNumberOccupants: int = ""
    maxNumberOfPets: int = ""
    unitAddress: UnitAddress = ""
    isFurnished: bool = ""
    isCorporateRented: bool = ""
    unitSpaces: UnitSpaces = ""

class Building:
    """
       Response model for Building Json
    """
    communityId: str = ""
    externalId: str = ""
    locationId: str = ""
    createdAt: str = ""
    updatedAt: str = ""
    name: str = ""
    type: str = "building"

    def __init__(self, communityId, externalId, locationId:str="", createdAt:str="", updatedAt:str="", name: str="", type:str = "building"):
        self.communityId = communityId
        self.externalId = externalId
        self.locationId = locationId
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
    name: str = ""
    type: str = "apartment"
    businessPurpose:str = "unit"
    parentIdExternal:str = ""
    parentId:str = ""
    bedroomsCount: str = ""
    bathroomsCount: str = ""
    occupantsCount: str = ""
    petsCount: str = ""

    def __init__(self, communityId, externalId, locationId:str="", createdAt:str="", name:str="", type:str = "apartment", businessPurpose:str= "unit", parentIdExternal:str="", parentId:str="", bedroomsCount: str = "", bathroomsCount: str = "", occupantsCount: str = "", petsCount: str = ""):
        self.communityId = communityId
        self.externalId = externalId
        self.locationId = locationId
        self.createdAt = createdAt
        self.name = name
        self.type = type
        self.businessPurpose = businessPurpose
        self.parentIdExternal = parentIdExternal
        self.parentId = parentId
        self.bedroomsCount = bedroomsCount
        self.bathroomsCount = bathroomsCount
        self.occupantsCount = occupantsCount
        self.petsCount = petsCount

class LeasesActivityItem(BaseModel):
    date:str = ""
    eventType:str = ""
    description:str = ""
    comment:str = ""


class LeaseActivities(BaseModel):
    leasesActivity:List[LeasesActivityItem] = []


class Phone(BaseModel):
    """
    Base model for the leases.lease.customers.addreses.address.phone Entrata
    """
    phoneType: str = ""
    phoneNumber: str = ""
    countryCode: str = ""

class Address_details(BaseModel):
    """
    Base model for the leases.lease.customers.addreses.address Entrata
    """
    addressType: str = ""
    streetLine:str = ""
    postalCode:str = ""
    countryName:str = ""
    state:str = ""
    city:str = ""
    email:str = ""
    additionalEmail:str = ""


class Address(BaseModel):
    """
    Base model for the leases.lease.customers.customer.addresses Entrata
    """
    address: Address_details = {}


class Customer_details(BaseModel):
    """
    Base model for the leases.lease.customers.customer[0] Entrata
    """
    id:str = ""
    customerType:str = ""
    firstName:str = ""
    lastName:str = ""
    nameFull:str = ""
    emailAddress:str = ""
    leaseCustomerStatus:str = ""
    relationshipName:str = ""
    dateOfBirth:str = ""
    idType:str = ""
    idNumber:str = ""
    addresses: Address = {}
    phone: Phone = {}
    moveInDate:str = ""
    moveOutDate:str = ""


class Customer(BaseModel):
    """
    Base model for the leases.lease.customers.customer Entrata
    """
    customer: List[Customer_details] = []


class LeaseInterval_details(BaseModel):
    """
    Base model for the leases.lease.leasesinterval[0] Entrata
    """
    id:str = ""
    startDate: str = ""
    endDate: str = ""
    leaseIntervalTypeId: str = None
    leaseIntervalTypeName:str = None
    leaseIntervalStatusTypeId:str = None
    leaseIntervalStatusTypeName:str = None
    intervalDateTime:str = ""
    leaseApprovedOn:str = ""
    applicationCompletedOn:str = ""
    applicationId:str = ""


class LeaseInterval(BaseModel):
    """
    Base model for the leases.lease.leasesinterval Entrata
    """
    leaseInterval: List[LeaseInterval_details] = []


class Lease(BaseModel):
    """
    Response model for leases.lease Entrata
    """
    id: str = ""
    leaseStatusTypeId:str = ""
    originalLeaseStartDate:str = ""
    parentLeaseId:str = ""
    parentUnitNumberCache:str = ""
    leaseSubStatus:str = ""
    leaseType:str = ""
    transferLeaseId:str = ""
    transferLeasePropertyId:str = ""
    propertyId:str = ""
    moveInDate:str = ""
    noticeDate:str = ""
    moveOutDate:str = ""
    moveOutReason:str = ""
    transferDate:str = ""
    propertyName:str = ""
    leaseIntervalStatus:str = ""
    occupancyTypeId:str = ""
    occupancyType:str = ""
    isMonthToMonth:str = ""
    leaseIntervalId:str = ""
    buildingId:str = ""
    buildingName:str = ""
    floorPlanId:str = ""
    floorPlanName:str = ""
    unitId:str = ""
    unitNumberSpace:str = ""
    unitSpaceId:str = ""
    spaceConfiguration:str = ""
    terminationStartDate:str = ""
    collectionsStartDate:str = ""
    leaseIntervals: LeaseInterval = {}
    customers: Customer = {}
    contract:dict = {}
    pets:dict = {}
    scheduledCharges:dict = {}
    specials:dict = {}
    leaseActivities:LeaseActivities = {}
    roommates:dict = {}
    arTransactions:dict = {}


class Leases(BaseModel):
    """
    Response model for leases Entrata
    """
    lease: List[Lease] = []


class AvailableHour(BaseModel):
    """
    Response model PropertyCalendarAvailability.AvailableHours.AvailableHour for Tour Availability
    """
    date: str = ""
    startTime: str = ""
    endTime: str = ""


class AvailableHours(BaseModel):
    """
    Response model PropertyCalendarAvailability.AvailableHours for Tour Availability
    """
    availableHour: List[AvailableHour] = []


class PropertyCalendarAvailability(BaseModel):
    """
    Response model for Tour Availability
    """
    availableHours: AvailableHours = None

class TourScheduling(BaseModel):
    """
    Response model for Book Tour
    """
    id: str = ""
    applicationId: str = ""
    applicantId: str = ""
    status: str = ""
    
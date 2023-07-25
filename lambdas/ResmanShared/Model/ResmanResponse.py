from typing import List, Optional, Union

from pydantic import BaseModel, Field, NonNegativeInt


class Identification(BaseModel):
    _IDValue: str = Field(..., alias='@IDValue')
    _OrganizationName: str = Field(..., alias='@OrganizationName')
    _IDType: str = Field(..., alias='@IDType')

class Address(BaseModel):
    _AddressType: str = Field(..., alias='@AddressType')
    AddressLine1: str = None
    AddressLine2: str = None
    City: str = None
    State: str = None
    PostalCode: str = None
    Country: str = None

class Unit(BaseModel):
    Identification: Identification
    MarketingName: str
    UnitType: str
    UnitBedrooms: str
    UnitBathrooms: str
    MinSquareFeet: str
    MaxSquareFeet: str
    MarketRent: str
    UnitEconomicStatus: str
    UnitOccupancyStatus: str
    UnitLeasedStatus: str
    FloorplanName: str
    BuildingName: str
    Address: Address

class Units(BaseModel):
    Unit: Unit

class StartDate(BaseModel):
    _Month: str = Field(..., alias='@Month')
    _Day: str = Field(..., alias='@Day')
    _Year: str = Field(..., alias='@Year')

class EndDate(BaseModel):
    _Month: str = Field(..., alias='@Month')
    _Day: str = Field(..., alias='@Day')
    _Year: str = Field(..., alias='@Year')

class DateRange(BaseModel):
    StartDate: StartDate
    EndDate: EndDate

class MITSOfferTermItem(BaseModel):
    EffectiveRent: str
    Term: str
    DateRange: Optional[DateRange]

class Pricing(BaseModel):
    MITS_OfferTerm: List[MITSOfferTermItem] = Field(..., alias='MITS-OfferTerm')

class EffectiveRent(BaseModel):
    _Avg: str = Field(..., alias='@Avg')
    _Min: str = Field(..., alias='@Min')
    _Max: str = Field(..., alias='@Max')

class ConcessionItem(BaseModel):
    _Active: str = Field(..., alias='@Active')
    Value: str
    Term: str
    DescriptionHeader: str

class ValueRange(BaseModel):
    _Exact: str = Field(..., alias='@Exact')

class Amount(BaseModel):
    _AmountType: str = Field(..., alias='@AmountType')
    ValueRange: ValueRange

class Deposit(BaseModel):
    _DepositType: str = Field(..., alias='@DepositType')
    Amount: Amount
    Description: str
    PercentRefundable: str
    PortionRefundable: str

class Availability(BaseModel):
    VacancyClass: str

class ILSUnitItem(BaseModel):
    _IDValue: str = Field(..., alias='@IDValue')
    _OrganizationName: str = Field(..., alias='@OrganizationName')
    _IDType: str = Field(..., alias='@IDType')
    Units: Units
    Pricing: Optional[Pricing]
    EffectiveRent: Optional[EffectiveRent]
    Concession: List[ConcessionItem]
    Deposit: Deposit
    FloorLevel: str
    Availability: Availability


class Property(BaseModel):
    PropertyID: dict = None
    ILS_Identification: dict = None
    Information: dict = None
    Fee: dict = None
    Concession: Union[dict, list] = None
    Amenity: List = None
    Building: List = None
    Floorplan: List = None
    ILS_Unit: List[ILSUnitItem]
    Utility: dict = None
    Policy: dict = None

class PhysicalProperty(BaseModel):
    Property: Property


class Response(BaseModel):
    PhysicalProperty: PhysicalProperty


class ResMan(BaseModel):
    MethodName: str = None
    Status: str = None
    AccountID: int = None
    PropertyID: str = None 
    Response: Response


class UnitResponse(BaseModel):
    ResMan: ResMan
from typing import List
from pydantic import BaseModel


class Resident(BaseModel):
    LeaseID: str = None
    BillingAccountID: str = None
    ParentLeaseGroupID: str = None
    PersonID: str = None
    FirstName: str = None
    LastName: str = None
    Unit: str = None
    Building: str = None
    Email: str = None
    MobilePhone: str = None
    HomePhone: str = None
    WorkPhone: str = None
    Birthdate: str = None
    LeaseStartDate: str = None
    LeaseEndDate: str = None
    MoveInDate: str = None
    MoveOutDate: str = None
    Rent: str = None
    DepositsHeld: str = None
    HouseholdStatus: str = None
    MainContact: bool = True
    IsMinor: bool = False
    AlternateContacts: List = []
    Pets: List = []


class CurrentResidentResponse(BaseModel):
    Residents: List[Resident] = []
    MethodName: str
    Status: str
    AccountID: int
    PropertyID: str

class LeasesHistory(BaseModel):
    LeaseID: str = None
    LeaseStartDate: str = None
    LeaseEndDate: str = None
    Status: str = None

class Person(BaseModel):
    ParentLeaseGroupID: str = None
    PersonID: str = None
    LeaseID: str = None
    FirstName: str = None
    LastName: str = None
    Birthdate: str = None
    Unit: str = None
    Building: str = None
    Email: str = None
    MobilePhone: str = None
    HomePhone: str = None
    WorkPhone: str = None
    LeaseStartDate: str = None
    LeaseEndDate: str = None
    MoveInDate: str = None
    MoveOutDate: str = None
    Status: str = None
    ApprovalStatus: str = None
    MainContact: bool = False
    Leases: List[LeasesHistory] = None


class LeaseResponse(BaseModel):
    People: List[Person] = []
    MethodName: str = None
    Status: str = None
    AccountID: int = None
    PropertyID: str = None

class Prospects(BaseModel):
    Name: str = None
    ID: str = None
    AvailableForOnlineMarketing: str = None
    IsActive: str = None

class ProspectResponse(BaseModel):
    ProspectSources: List[Prospects] = []
    
class Name(BaseModel):
    FirstName: str
    MiddleName: str = None
    LastName: str


class Phone(BaseModel):
    PhoneNumber: str


class IdentificationItem(BaseModel):
    IDType: str = Field(..., alias='@IDType')
    IDValue: str = Field(..., alias='@IDValue')
    OrganizationName: str = Field(..., alias='@OrganizationName')


class Customer(BaseModel):
    Type: str = Field(..., alias='@Type')
    Name: Name
    Phone: Phone
    Email: str
    Identification: List[IdentificationItem]


class Customers(BaseModel):
    Customer: Customer


class DesiredRent(BaseModel):
    Exact: str = Field(..., alias='@Exact')


class DesiredNumBedrooms(BaseModel):
    Exact: str = Field(..., alias='@Exact')


class CustomerPreferences(BaseModel):
    DesiredFloorplan: str
    DesiredRent: DesiredRent
    DesiredNumBedrooms: DesiredNumBedrooms
    DesiredLeaseTerms: str
    Comments: str


class AgentID(BaseModel):
    IDValue: str = Field(..., alias='@IDValue')


class AgentName(BaseModel):
    FirstName: str
    LastName: str


class Agent(BaseModel):
    AgentID: AgentID
    AgentName: AgentName


class Event(BaseModel):
    EventType: str = Field(..., alias='@EventType')
    EventDate: str = Field(..., alias='@EventDate')
    Agent: Agent
    FirstContact: str
    TransactionSource: str


class Events(BaseModel):
    Event: Event


class Prospect(BaseModel):
    Customers: Customers
    CustomerPreferences: CustomerPreferences
    Events: Events


class Prospects(BaseModel):
    Prospect: Prospect


class LeadManagement(BaseModel):
    Prospects: Prospects


class Response(BaseModel):
    LeadManagement: LeadManagement


class ResMan(BaseModel):
    MethodName: str
    Status: str
    AccountID: str
    PropertyID: str
    Response: Response


class ResmanResponse(BaseModel):
    ResMan: ResMan


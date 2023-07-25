from typing import List, Optional

from pydantic import BaseModel, Field


class IdentificationItem(BaseModel):
    IDType: Optional[str] = Field(..., alias='@IDType')
    IDValue: Optional[str] = Field(..., alias='@IDValue')
    OrganizationName: Optional[str] = Field(..., alias='@OrganizationName')


class Name(BaseModel):
    FirstName: str
    MiddleName: str = None
    LastName: str


class Address(BaseModel):
    AddressType: str = Field(..., alias='@AddressType')


class Phone(BaseModel):
    PhoneNumber: str


class Customer(BaseModel):
    Type: str = Field(..., alias='@Type')
    Identification: List[IdentificationItem]
    Name: Name
    Address: Address
    Phone: Phone
    Email: str


class Customers(BaseModel):
    Customer: Customer


class DesiredRent(BaseModel):
    Exact: Optional[str] = Field(..., alias='@Exact')


class DesiredNumBedrooms(BaseModel):
    Exact: Optional[str] = Field(..., alias='@Exact')


class CustomerPreferences(BaseModel):
    TargetMoveInDate: Optional[str]
    DesiredFloorplan: Optional[str] = None
    DesiredRent: DesiredRent
    DesiredNumBedrooms: DesiredNumBedrooms
    DesiredLeaseTerms: str
    Comments: str


class EventID(BaseModel):
    IDType: Optional[str] = Field(..., alias='@IDType')
    IDValue: Optional[str] = Field(..., alias='@IDValue')
    OrganizationName: Optional[str] = Field(..., alias='@OrganizationName')


class AgentID(BaseModel):
    IDValue: str = Field(..., alias='@IDValue')


class AgentName(BaseModel):
    FirstName: str
    LastName: str


class Agent(BaseModel):
    AgentID: AgentID
    AgentName: AgentName


class EventItem(BaseModel):
    EventType: str = Field(..., alias='@EventType')
    EventDate: str = Field(..., alias='@EventDate')
    EventID: EventID
    Agent: Agent
    FirstContact: str
    Comments: Optional[str] = None
    TransactionSource: Optional[str] = None


class Events(BaseModel):
    Event: List[EventItem]


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


class ResmanUpdateResponse(BaseModel):
    ResMan: ResMan

    
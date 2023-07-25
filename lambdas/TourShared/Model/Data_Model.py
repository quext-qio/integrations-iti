from enum import Enum
from typing import List
from pydantic import BaseModel


class AppointmentData:
    firstName: str
    lastName: str
    email: str
    phone: str
    layout: List[str]
    priceCeiling: str
    moveInDate: str
    notes: str
    start: str
    source: str


class BasePlatformData:
    communityUUID: str
    customerUUID: str


class PlatformData:
    token: str
    provider_key: str
    platform: str
    issuer: str
    subject: str
    bookable: str
    form_id: str


class ScheduleTourFormData:
    appointmentData: AppointmentData
    platformData: BasePlatformData


class TourAvailabilityData:
    fromDate: str
    toDate: str


class TourAvailabilityFormData:
    timeData: TourAvailabilityData
    platformData: BasePlatformData

class AvailableSlot(BaseModel):
    start: str
    end: str
    length_in_mins: str = None

class Data(BaseModel):
    availableTimes: List = []

class Platform_Type(Enum):
    NONE = 0
    FUNNEL = 1
    PERIODIC = 2


class Layout_Type(Enum):
    NONE = 0
    ONE_BEDROOM = 1
    TWO_BEDROOM = 2
    THREE_BEDROOM = 3
    FOUR_BEDROOM = 4
    FIVE_BEDROOM = 5
    STUDIO = 6
    LOFT = 7
    OTHERS = 8


class HTTP_Request_Type(Enum):
    GET = 0
    POST = 1


class Environment_Type(Enum):
    DEVELOPMENT = 0
    PRODUCTION = 1
    STAGING = 2


response_header = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, HEAD, OPTIONS'
}

from datetime import date
from typing import List

from pydantic import BaseModel


class Property(BaseModel):
    name: str = None
    address: str = None
    address2: str = None
    city: str = None
    state: str = None
    postal: str = None
    email: str = None
    phone: str = None
    speed_dial: str = None
    fax: str = None

class Models(BaseModel):
    property_id: str = None
    property_name: str = None
    model_type: str = None
    unit_type_name: str = None
    unit_type_desc: str = None
    beds: float = None
    baths: float = None
    total_units: int = None
    available: int = None
    unit_type_first_avail: date = None
    unit_market_rent_all: float = None
    unit_market_rent_avail: float = None
    market_rent: float = None
    sqft_model_base: float = None
    sqft: float = None
    sqft_min_all: int = None
    sqft_max_all: int = None
    sqft_min_avail: int = None
    sqft_max_avail: int = None
    sqft_min_report: int = None
    sqft_max_report: int = None
    sqft_range: int = None
    website: str = None
    virtual_tour_url: str = None
    virtual_tour: str = None
    floorplan: str = None
    floorplan_alt_text: str = None

class Units(BaseModel):
    property_id: str = None
    property_name: str = None
    building: str = None
    floor: str = None
    unit_id: str = None
    unit_number: str = None
    available_boolean: str = None
    is_available: int = None
    available: int = None
    available_date: date = None
    unit_status: str = None
    model_type: str = None
    unit_type_name: str = None
    unit_type_desc: str = None
    beds: str = None
    baths: str = None
    market_rent: float = None
    market_rent_amount: float = None
    sqft: int = None


class UnitResponse(BaseModel):
    provenance: List[str]
    property: Property
    models: List[Models]
    units: List[Units]


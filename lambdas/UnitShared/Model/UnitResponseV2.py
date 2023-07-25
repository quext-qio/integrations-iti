from pydantic import BaseModel
from typing import List


class SquareFeetInfo(BaseModel):
    sqft_min_all: int = 0
    sqft_max_all: int = 0
    sqft_min_avail: int = 0
    sqft_max_avail: int = 0
    sqft_min_report: int = 0
    sqft_max_report: int = 0
    
    
class AvailableInfo(BaseModel):
    qavailable_date:str = ""
    qavailable_bit:bool = None
    qunit_hidden:bool = None
    qunit_status: str = ""
    qunit_vacant: bool = None


class QUnit(BaseModel):
    community_id: str = ""
    unit_id: str = ""
    qavailable_object: object = None


class Unit(BaseModel):
    community_id: str = ""
    building: str = ""
    floor: str = ""
    unit_id: str = ""
    unit_number: str = ""
    qavailable_info: AvailableInfo = AvailableInfo()
    available_date: str = ""
    available_boolean: bool = None
    unit_type_name: str = ""
    unit_type_desc: str = ""
    beds: str = ""
    baths: str = ""
    market_rent: float = 0.0
    sqft_min: float = 0.0
    sqft_max: float = 0.0
    
    
class MarketRent(BaseModel):
    min_rent_all: float = 0.0
    min_rent_available: float = 0.0


class URLS(BaseModel):
    files: list = []
    website: str = ""
    virtual_tour_url: str = ""
    virtual_tour: str = ""
    floorplan: str = ""
    floorplan_alt_text: str = ""
    

class UnitType(BaseModel):
    community_id: str = ""
    unit_type_name: str = ""
    unit_type_desc: str = ""
    beds: float = 0.0
    baths: float = 0.0
    total_units: int = 0
    total_available_units: int = 0
    unit_type_first_available_date: str = ""
    market_rent: MarketRent = MarketRent()
    urls: URLS = URLS()
    sqft_model_base: float = 0.0 #add this attribute in Square Feet Info
    sqft_info: SquareFeetInfo = SquareFeetInfo()
    sqft_range: str = ""
    available_units: List[Unit] = []
    unavailable_units: List[Unit] = []
    units: List[Unit] = []
    qunits: List[QUnit] = []


class Community(BaseModel):
    provenance: List[str] = []
    localControl: str = ""
    address: str = ""
    address2: str = ""
    city: str = ""
    state_province : str = ""
    postal: str = ""
    email: str = ""
    phone: str = ""
    country_code: str = "+1"
    speed_dial: str = ""
    fax: str = ""
    source_system: str = ""
    unit_types: List[UnitType] = []
    models_dict: dict = {}


class UnitResponse(BaseModel):
    communities: List[Community]
    prop_dict: dict = {}

class UnitErrorResponse(BaseModel):
    community_id: str = ""
    error_message: str = ""
    partner_name: str = ""

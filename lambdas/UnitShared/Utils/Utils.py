from enum import Enum

from pydantic import BaseModel
from datetime import date, datetime, timedelta
from VendorShared.Model.ServiceRequest import ServiceRequest
from ExceptionHandling.Model.Exceptions import GatewayError, ValidationError
from VendorShared.Utilities.VendorConstants import VendorConstants, PartnerConstants
from typing import List
import dateutil.parser
import os, logging



class AvailableUnits(BaseModel):
    """
    Schema for Available Units Object

    Args:
        BaseModel (_type_): _description_
    """
    unitHoldUntil:str = ""
    qReadyToShowDate:str = "" 
    qReadyToShow:str = ""
    qUnitVisible:bool = False
    qUnitVacatedDate:str = ""    
    
    
class Schema(Enum):
    NONE = 0
    RESMAN = 1,
    REALPAGE = 2,
    ENTRATA= 3
   

class PostResponse:
    
    def __init__(self, service_request: ServiceRequest, response:dict, partner_name: str) -> None:
        """        
        Args:
            service_request (ServiceRequest): Servicerequest object
            response (dict): Dict
        """
        self.service_request = service_request
        self.response = response
        self.partner_name = partner_name
    
    def getLocalControlItems(self, _type: Enum = Schema.NONE):
        """ Returns The LocalControl Value based on the 
            Enum choice

        Args:
            _type (Enum, optional): Enum. Defaults to Schema.NONE.

        Returns:
            _type_: Dict
        """
        return PartnerSchema.get(_type) 
    
    def available_date(self, unit:AvailableUnits):
        """ Returns the available date for the units by evaluating the 
            below conditions

        Args:
            unit (AvailableUnits): AvailableUnits object

        Returns:
            _type_: _description_
        """
        unit_hold_until = unit.unitHoldUntil and dateutil.parser.parse(unit.unitHoldUntil) or None # this needs to be changed
        qready_to_show_date = unit.qReadyToShowDate and dateutil.parser.parse(unit.qReadyToShowDate) or unit.qReadyToShowDate # qready_to_show_date
        qready_to_show = unit.qReadyToShow 
        qunit_vacated_date = unit.qUnitVacatedDate and dateutil.parser.parse(unit.qUnitVacatedDate) or unit.qUnitVacatedDate       
        today = datetime.today()
    
        if unit_hold_until and unit_hold_until > today and unit_hold_until >= qready_to_show_date:
            return unit_hold_until
    
        elif qready_to_show_date: 
            if qready_to_show_date > today and (qready_to_show == "false" or not qready_to_show):
                return qready_to_show_date +  timedelta(days=int(os.getenv("AVAILABILITY_MAKEREADY_BUFFER", 2)))  #from made ready buffer
            elif qready_to_show_date > today and qready_to_show == "true":
                return today
            elif qready_to_show_date < today and (qready_to_show == "true" or not qready_to_show):
                return today
            elif qready_to_show_date < today and qready_to_show == "false":
                return today + timedelta(days=int(os.getenv("AVAILABILITY_MAKEREADY_MISSING_BUFFER", 2))) # from made_ready_missing_buffer
            
        elif not qready_to_show_date:
            if not qunit_vacated_date:
                return None
            elif qunit_vacated_date < today:
                return today + timedelta(days=int(os.getenv("AVAILABILITY_MAKEREADY_MISSING_BUFFER", 2)))
            elif qunit_vacated_date >= today:
                return qunit_vacated_date + timedelta(days=int(os.getenv("AVAILABILITY_MAKEREADY_MISSING_BUFFER", 2)))

    def available_bit(self, date, payload:dict={}):
        """ Returns the Boolean value based on the available date 
            returned from the available_date function

        Args:
            date (_type_): datetime
            payload (dict, optional): Request Body. Defaults to {}.

        Returns:
            _type_: boolean
        """
        start_date = datetime_object_string(dateutil.parser.parse(payload["available_start_date"]) if ("available_start_date" in payload and len(payload.get("available_start_date").strip())) != 0 else datetime.today())     
        end_date = datetime_object_string(dateutil.parser.parse(payload["available_end_date"]) if "available_end_date" in payload and len(payload.get("available_end_date").strip()) != 0 else  datetime.today() + timedelta(int(os.getenv("AVAILABILITY_INCLUDE_FUTURE_DAYS", 90))))
        
        if  isinstance(date, str) and len(date) > 0 :
            if common_format(start_date) <= common_format(date) <= common_format(end_date):
                return True
            else:
                return False 
        else:
            return False
        
    def calculate_sqft(self, model_obj: object):
        """
        This method is to calculate the values for SquareFeetInfo model
        """
        available_sqft_min = []
        available_sqft_max = []
        unavailable_sqft_min = []
        unavailable_sqft_max = []
        available_rent = []
        unavailable_rent = []
        # Available Unit
        for unit in model_obj.available_units:
            available_sqft_min.append(unit.sqft_min)
            available_sqft_max.append(unit.sqft_max)
            available_rent.append(unit.market_rent)
        # Unavailable Unit
        for unit in model_obj.unavailable_units:
            unavailable_sqft_min.append(unit.sqft_min)
            unavailable_sqft_max.append(unit.sqft_max)
            unavailable_rent.append(unit.market_rent)
        min_sqft_all = unavailable_sqft_min + available_sqft_min
        max_sqft_all = unavailable_sqft_max + available_sqft_max
        unavailable_rent = unavailable_rent + available_rent
        model_obj.sqft_info.sqft_min_all = min_sqft_all and min(min_sqft_all) or 0.0
        model_obj.sqft_info.sqft_min_avail = available_sqft_min and min(available_sqft_min) or 0.0
        model_obj.sqft_info.sqft_max_all = max_sqft_all and max(max_sqft_all) or available_sqft_min and max(available_sqft_min) or 0.0
        model_obj.sqft_info.sqft_max_avail = available_sqft_max and max(available_sqft_max) or available_sqft_min and max(available_sqft_min) or 0.0
        model_obj.sqft_info.sqft_min_report = model_obj.sqft_info.sqft_min_all and model_obj.sqft_info.sqft_min_all or model_obj.sqft_model_base
        model_obj.sqft_info.sqft_max_report = model_obj.sqft_info.sqft_max_all and model_obj.sqft_info.sqft_max_all or model_obj.sqft_model_base
        model_obj.sqft_range = model_obj.sqft_info.sqft_max_report and model_obj.sqft_info.sqft_max_report or model_obj.sqft_info.sqft_max_report and str(model_obj.sqft_info.sqft_min_report)+"-"+str(model_obj.sqft_info.sqft_max_report) or 0     
        model_obj.market_rent.min_rent_all = unavailable_rent and min(unavailable_rent) or 0.0
        model_obj.market_rent.min_rent_available = available_rent and min(available_rent) or 0.0
    
    def build_response(self):
        """ Fixing the LocalControl, SourceSystem, available_units, unavailable_units values 
            in the response dict

        Returns:
            _type_: object
        """
        
        _response = self.response
        _partner_name = self.partner_name
    
        
        for i in _response.communities:         
            i.localControl = self.getLocalControlItems(PartnerMapping.get(_partner_name.lower(), Schema.NONE))
            i.source_system = _partner_name.capitalize()            
            if hasattr(i, "models_dict"):
                delattr(i, "models_dict")
                
            for j in i.unit_types:
                available_units, unavailable_units = [] , []                              
                for unit, qunit in zip(j.units, j.qunits):
                    date_time_object = self.available_date(qunit.qavailable_object)
                    if date_time_object is not None:
                        format_date_str = date_time_object.strftime("%Y-%m-%d %H:%M:%S.%f")
                        unit.qavailable_info.qavailable_date = string_to_utc(format_date_str, "%Y-%m-%d %H:%M:%S.%f")
                    else:
                        unit.qavailable_info.qavailable_date = ""
                    unit.qavailable_info.qavailable_bit = self.available_bit(unit.qavailable_info.qavailable_date, self.service_request.request.payload)
                    unit.qavailable_info.qunit_hidden = qunit.qavailable_object.qUnitVisible
                    unit.available_boolean = unit.qavailable_info.qavailable_bit
                    if unit.available_date and isinstance(unit.available_date, str):
                        unit.available_date = string_to_utc(unit.available_date, date_formate_mapping.get(_partner_name.lower()))
                    elif unit.available_date and isinstance(unit.available_date, object):
                        string_date = unit.available_date.strftime("%Y-%m-%d")
                        unit.available_date = string_to_utc(string_date, date_formate_mapping.get(_partner_name.lower()))
                    if not self.service_request.request.payload.get("filter_on_availability") and not unit.qavailable_info.qavailable_bit:
                        unavailable_units.append(unit)                
                    elif unit.qavailable_info.qavailable_bit:
                        available_units.append(unit)                        
                j.total_units = len(j.units) 
                j.total_available_units = len(available_units)
                j.available_units = available_units
                j.unavailable_units = unavailable_units
                self.calculate_sqft(j)
                delattr(j, "units")                    
                delattr(j, "qunits")
        
        return _response


def common_format(date_string):
    """
    diffrent string formate to common datetime obeject
    """
    datetime_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    return datetime.strptime(datetime_obj.strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

def string_to_utc(date_string, date_format):
    """
    string to UTC format
    """
    date_object = datetime.strptime(date_string, date_format)
    UTC_date_string = date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
    return UTC_date_string

def datetime_object_string(datetime_object):
    """
    convert datetime object to string format
    """
    return datetime_object.strftime("%Y-%m-%dT%H:%M:%SZ")

PartnerMapping = {
    "realpage" : Schema.REALPAGE
}

PartnerSchema = {
    Schema.NONE: {
            "fields" : []
    },
    Schema.REALPAGE: {
            "fields" : ["floorplan_url","floorplan_alt_desc", "virtual_tour_url"]
    }    
}

date_formate_mapping = {
    PartnerConstants.RESMAN.lower(): VendorConstants.RESMAN_DATE_FORMAT,
    PartnerConstants.ENTRATA.lower(): VendorConstants.ENTRATA_DATE_FORMAT,
    PartnerConstants.NEWCO.lower(): VendorConstants.NEWCO_DATE_FORMAT,
    PartnerConstants.REALPAGE.lower(): VendorConstants.REALPAGE_DATE_FORMAT
}

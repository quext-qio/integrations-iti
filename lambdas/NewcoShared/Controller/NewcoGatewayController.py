from contextlib import closing
import types
import os
from DataPushPullShared.Utilities.QueryController import QueryController
from NewcoShared.Utilities.NewcoConstants import NewcoConstants
from TourShared.Model.Data_Model import TourAvailabilityData
from VendorShared.Controller.VendorGatewayController import VendorGatewayController
from VendorShared.Model.ServiceRequest import ServiceRequest
from DataPushPullShared.Utilities.QueryController import QueryController
from UnitShared.Utils.Utils import AvailableUnits
from UnitShared.Model.UnitResponseV2 import UnitResponse, Community, UnitType, Unit, QUnit, AvailableInfo, SquareFeetInfo, MarketRent, URLS
from VendorShared.Utilities.VendorConstants import PartnerConstants
from Utils.ConditionGenerator import ConditionGenerator
from Utils import CustomLogger

logging = CustomLogger.logger


class NewcoGatewayController(VendorGatewayController):
    """
    NewcoGatewayController class for handling Newco related communication and data transformations
    """
    __query_read_obj = QueryController()

    def get_unit_availability(self, service_request: ServiceRequest):
        """
        Get Unit and Price information
        """
        logging.debug("Getting unit availability from Newco")
        parameters = {NewcoConstants.NEWCO_PROPERTY_ID:
                          service_request.platformdata[NewcoConstants.PLATFORMDATA][NewcoConstants.COMMUNITYID]}

        with closing(service_request.outgoing.sql.get(NewcoConstants.NEWCO_EXTERNAL).session()) as session:
            # Get the property details data...
            property = self.__get_property_data(service_request, session, parameters)

        response = UnitResponse(**{"communities": [property]})
        delattr(response,'prop_dict')
        return response

    def get_leases(self, service_request: ServiceRequest):
        """
        Get Leasing information
        """
        pass

    def get_locations(self, service_request: ServiceRequest):
        """
        Get location information
        """
        pass

    def get_residents(self, service_request: ServiceRequest):
        """
        Get residents information
        """
        pass

    def post_guestcards(self, service_request: ServiceRequest):
        """
        Get guest card information
        """
        pass
        
    def get_tour_availabilities(self, service_request: ServiceRequest, tour_availability_data: TourAvailabilityData):
        """
        Get tour availabilities information
        """
        pass

    def book_tour_appointment(self, service_request: ServiceRequest, appointmentData = None):
        """
        Post book tour appointment information
        """
        pass

    def __get_property_data(self, service_request: ServiceRequest, session: object, parameters: dict) -> dict:
        """
        Get property information
        """
        path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_PROPERTY_QUERY
        output = self.__query_read_obj.read_query(service_request, path, NewcoConstants.NEWCO_QUERY_CACHE,
                                                  NewcoConstants.NEWCO_PROPERTY_QUERY, 0.0)
        result = session.execute(output, parameters)
        property = {}
        for row in result:
            _row_dict = {k: v for k, v in row.items()}     
            _row = types.SimpleNamespace(**_row_dict)                   
            community = Community()   
            community.provenance =  ["Newco", os.getenv("Environment", "")]         
            community.fax = _row.fax if hasattr(_row, "fax") and _row.fax is not None else ""
            community.speed_dial = _row.speed_dial if hasattr(_row, "speed_dial") and _row.speed_dial is not None else ""
            community.address = _row.address if hasattr(_row, "address") and _row.address is not None else ""
            community.phone = _row.phone if _row.phone is not None and hasattr(_row, "phone") else ""
            community.country_code = _row.country_code if hasattr(_row, "country_code") and _row.country_code is not None else "+1"
            community.city = _row.city if _row.city is not None and hasattr(_row, "city") else ""
            community.email = _row.email if _row.email is not None and hasattr(_row, "email") else ""
            community.state_province = _row.state if _row.state is not None and hasattr(_row, "state")else ""
            property = community
            # Get the apartment models data...
            model=self.__get_models_data(service_request, session, parameters)
        property.unit_types = model
        return property

    def __get_models_data(self, service_request: ServiceRequest, session: object, parameters: dict) -> list:
        """
        Get models information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.__query_read_obj.read_query(service_request, base_query_path,
                                                                  NewcoConstants.NEWCO_QUERY_CACHE,
                                                                  NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        model_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_MODELS_QUERY
        newco_units_models_query = self.__query_read_obj.read_query(service_request, model_query_path,
                                                                    NewcoConstants.NEWCO_QUERY_CACHE,
                                                                    NewcoConstants.NEWCO_MODELS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_models_query
        result = session.execute(output, parameters)
        models = []
        for row in result:
            _row_dict = {k: v for k, v in row.items()}     
            _row = types.SimpleNamespace(**_row_dict)                                                       
            model = UnitType() 
            model.community_id = _row.property_id if hasattr(_row, "property_id") and _row.property_id is not None else ""
            model.unit_type_name = _row.unit_type_name if hasattr(_row, "unit_type_name") and _row.unit_type_name is not None else ""
            model.unit_type_desc = _row.unit_type_desc if hasattr(_row, "unit_type_desc") and _row.unit_type_desc is not None else ""
            model.beds = _row.beds if hasattr(_row, "beds") and _row.beds is not None else 0.0
            model.baths = _row.baths if hasattr(_row, "baths") and _row.baths is not None else 0.0
            model.total_units = _row.total_units if hasattr(_row, "total_units") and _row.total_units is not None else 0
            model.urls = _row.urls if hasattr(_row, "urls") and _row.urls is not None else URLS()
            model.sqft_model_base = _row.sqft_model_base if hasattr(_row, "sqft_model_base") and _row.sqft_model_base is not None else None
            model.sqft_info = _row.sqft_info if hasattr(_row, "sqft_info") and _row.sqft_info is not None else SquareFeetInfo()
            model.sqft_range = _row.sqft_range if hasattr(_row, "sqft_range") and _row.sqft_range is not None  else ""  
            model.available_units = _row.available_units if hasattr(_row, "available_units") else []
            model.unavailable_units = _row.unavailable_units if hasattr(_row, "unavailable_units") else []
            model.units = _row.units if hasattr(_row, "units") else []                                       

            models.append(model)
        # Get the units data
        self.__get_units_data(service_request, session, parameters, models)
        return models

    def __get_units_data(self, service_request: ServiceRequest, session: object, parameters: dict,
                         model_obj: object) -> list:
        """
        Get units information
        """
        base_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_BASE_QUERY
        newco_units_base_query = self.__query_read_obj.read_query(service_request, base_query_path,
                                                                  NewcoConstants.NEWCO_QUERY_CACHE,
                                                                  NewcoConstants.NEWCO_BASE_QUERY, 0.0)
        units_query_path = NewcoConstants.QUERY_PATH + NewcoConstants.NEWCO_UNITS_UNITS_QUERY
        newco_units_units_query = self.__query_read_obj.read_query(service_request, units_query_path,
                                                                   NewcoConstants.NEWCO_QUERY_CACHE,
                                                                   NewcoConstants.NEWCO_UNITS_QUERY, 0.0)
        output = newco_units_base_query + newco_units_units_query
        if NewcoConstants.FILTER_ON_AVAILABILITY in service_request.request.payload and service_request.request.payload[
            NewcoConstants.FILTER_ON_AVAILABILITY]:
            output += NewcoConstants.IS_AVAILABLE
        result = session.execute(output, parameters)
        for row in result:
            _row_dict = {k: v for k, v in row.items()}     
            _row = types.SimpleNamespace(**_row_dict)                                        
            unit = Unit()
            qunit = QUnit()
            qunit.qavailable_object = AvailableUnits(#qReadyToShowDate=input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.MADE_READY_DATE],
                                         #qReadyToShow = input_dict[RealpageConstants.AVAILABILITY]['MadeReadyBit'],
                                         qUnitVacatedDate = str(_row.available_date) if hasattr(_row, "available_date") and _row.available_date is not None else "", 
                                         qUnitVisible = ConditionGenerator.generate_condition(_row.unit_status, "not in", PartnerConstants.NEWCO.upper()))            
            unit.community_id =_row.property_id if hasattr(_row, "property_id") and _row.property_id is not None else ""
            unit.building =_row.building if hasattr(_row, "building") and _row.building is not None else ""
            unit.floor =_row.floor if hasattr(_row, "floor") and _row.floor is not None else ""
            unit.unit_id =_row.unit_id if hasattr(_row, "unit_id") and _row.unit_id is not None else ""
            unit.unit_number =_row.unit_number if hasattr(_row, "unit_number") and _row.unit_number is not None else ""            
            unit.available_date =_row.available_date if hasattr(_row, "available_date") and _row.available_date is not None else ""            
            unit.unit_type_name =_row.unit_type_name if hasattr(_row, "unit_type_name") and _row.unit_type_name is not None else ""
            unit.unit_type_desc =_row.unit_type_desc if hasattr(_row, "unit_type_desc") and _row.unit_type_desc is not None else ""
            unit.beds =_row.beds if hasattr(_row, "beds") and _row.beds is not None else ""
            unit.baths =_row.baths if hasattr(_row, "baths") and _row.baths is not None else ""
            unit.market_rent = round(float(_row.market_rent), 2) if hasattr(_row, "market_rent") and _row.market_rent is not None else 0.0
            unit.sqft_min = round(float(_row.sqft), 2) if hasattr(_row, "sqft") and _row.sqft is not None else 0.0            
            
            for i in model_obj:
                if i.unit_type_name == unit.unit_type_name:
                    i.units.append(unit)
                    i.qunits.append(qunit)
                    break                  
        return


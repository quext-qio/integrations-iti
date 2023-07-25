from UnitShared.Model.UnitResponseV2 import UnitResponse, Community, UnitType, Unit, QUnit
from VendorShared.Utilities.VendorConstants import PartnerConstants
from RealpageShared.Utilities.RealpageConstants import RealpageConstants
from UnitShared.Utils.Utils import AvailableUnits
import logging
from Utils.ConditionGenerator import ConditionGenerator
import os


class RealPageUnitResponse:
    '''
    Class to format Unit availability response for Realpage
    '''

    def unit_availability_response(self, input_dict: dict):
        '''
        Method to format the response from Realpage endpoint
        '''
        property_list = []
        property_dict = {}
        
        # Creating unit response model object
        res_obj = UnitResponse(communities=property_list, prop_dict=property_dict)
        for data in input_dict:

            if data[RealpageConstants.PROPERTY_NUMBER_ID] not in res_obj.prop_dict:
                units_dict = self.create_unit_obj(data) #unit 
                unit_obj = [units_dict['unit_obj']]        
                qunit_obj = [units_dict['qunit_obj']]
                model_obj = self.create_model_obj(unit_obj, qunit_obj, data) #unit_type
                model_dict={}
                model_dict[data[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]] = model_obj
                property_obj = self.create_property_obj(model_dict,data) #community
                res_obj.prop_dict[data[RealpageConstants.PROPERTY_NUMBER_ID]] = property_obj
            else:
                #check if the model is already present
                md = res_obj.prop_dict[data[RealpageConstants.PROPERTY_NUMBER_ID]].models_dict
                if data[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID] not in md.keys():
                    # Adding new model and unit inside property 
                    units_dict = self.create_unit_obj(data) #unit 
                    unit_obj = [units_dict['unit_obj']]        
                    qunit_obj = [units_dict['qunit_obj']]
                    model_dict={}
                    model_obj = self.create_model_obj(unit_obj, qunit_obj, data)
                    md[data[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]] = model_obj
                else:
                    # Adding new unit in already existing model
                    units_dict = self.create_unit_obj(data) #unit 
                    unit_obj = units_dict['unit_obj']
                    qunit_obj = units_dict['qunit_obj']
                    md[data[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]].units.append(unit_obj)
                    md[data[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]].qunits.append(qunit_obj)
        # Generate list of properties from property dict
        res_obj.communities = [value for value in res_obj.prop_dict.values()]
        for i in res_obj.communities:
            #Generate list of models within each property from model dict
            i.unit_types = [value for value in i.models_dict.values()]
        
        if hasattr(res_obj, "prop_dict"):
            delattr(res_obj, "prop_dict")
        logging.info(f"Response Object {res_obj}")   
        
        return res_obj

    def create_property_obj(self, model_dict, input_dict):
        # Method to create Community obj using model_dict and input data
        property_obj = Community(models_dict=model_dict)        
        property_obj.provenance = ["RealPage", os.getenv("Environment", "")]        
        property_obj.address = input_dict[RealpageConstants.ADDRESS][RealpageConstants.ADDRESS1]
        property_obj.city = input_dict[RealpageConstants.ADDRESS][RealpageConstants.CITY_NAME] 
        property_obj.state_province = input_dict[RealpageConstants.ADDRESS][RealpageConstants.STATE] 
        property_obj.postal = input_dict[RealpageConstants.ADDRESS][RealpageConstants.ZIP]        
        return property_obj

    def create_model_obj(self, unit_obj, qunit, input_dict):
        # Method to create Model obj using unit obj and input data
        model_obj = UnitType(units = unit_obj, qunits= qunit) 
        model_obj.community_id = input_dict[RealpageConstants.PROPERTY_NUMBER_ID]
        model_obj.unit_type_name = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]
        model_obj.beds = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BEDROOMS]
        model_obj.baths = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BATHROOMS]
        model_obj.sqft_model_base = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT]
        model_obj.urls.floorplan = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE]
        model_obj.urls.floorplan_alt_text = model_obj.unit_type_desc = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_NAME]
        return model_obj


    def create_unit_obj(self, input_dict):
        # Method to create units object from input
        unit_obj = Unit()
        # unit_obj.qavailable_object = AvailableUnits(qReadyToShowDate=input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.MADE_READY_DATE],
        #                                  qReadyToShow = input_dict[RealpageConstants.AVAILABILITY]['MadeReadyBit'],
        #                                  qUnitVacatedDate = input_dict[RealpageConstants.AVAILABILITY]['VacantDate'],
        #                                  qUnitVisible = ConditionGenerator.generate_condition(input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.UNITHOLDSTATUS], "in", PartnerConstants.REALPAGE.upper()))        
        unit_obj.community_id = input_dict[RealpageConstants.PROPERTY_NUMBER_ID]
        unit_obj.building = input_dict[RealpageConstants.ADDRESS][RealpageConstants.BUILDING_ID]
        unit_obj.floor = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.FLOOR_NUMBER]
        unit_obj.unit_id = input_dict[RealpageConstants.ADDRESS][RealpageConstants.UNIT_ID]
        unit_obj.unit_number = input_dict[RealpageConstants.ADDRESS][RealpageConstants.UNIT_NUMBER]
        unit_obj.available_date = input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.VACANTDATE]
        unit_obj.unit_type_name = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_ID]
        unit_obj.unit_type_desc = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_NAME]
        unit_obj.beds = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BEDROOMS]
        unit_obj.baths = input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BATHROOMS]
        # QUnit object to  calculate the AvailableUnits
        qunit_obj = QUnit()
        qunit_obj.community_id = unit_obj.community_id
        qunit_obj.unit_id = unit_obj.unit_id
        qunit_obj.qavailable_object = AvailableUnits(qReadyToShowDate=input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.MADE_READY_DATE],
                                         qReadyToShow = input_dict[RealpageConstants.AVAILABILITY]['MadeReadyBit'],
                                         qUnitVacatedDate = input_dict[RealpageConstants.AVAILABILITY]['VacantDate'],
                                         qUnitVisible = ConditionGenerator.generate_condition(input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.UNITHOLDSTATUS], "in", PartnerConstants.REALPAGE.upper()))  
        # Converting the Market_rent and Sqft value to float
        unit_obj.market_rent = round(float(input_dict[RealpageConstants.EFFECTIVE_RENT]), 2)
        unit_obj.sqft_min = round(float(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT]), 2)
        
        units_dict = {
            'unit_obj': unit_obj,
            'qunit_obj': qunit_obj
        }
        
        return units_dict
    

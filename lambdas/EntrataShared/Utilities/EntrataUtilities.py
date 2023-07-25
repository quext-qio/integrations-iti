from datetime import datetime
# import logging

from EntrataShared.Utilities.EntrataConstants import EntrataConstants
from UnitShared.Model.UnitResponseV2 import UnitResponse, Community, UnitType, SquareFeetInfo,\
                                            Unit, QUnit, URLS
from VendorShared.Utilities.VendorConstants import PartnerConstants
from Utils.ConditionGenerator import ConditionGenerator
from UnitShared.Utils.Utils import AvailableUnits
from DataPushPullShared.Utilities.Convert import Convert
from Utils import CustomLogger

logging = CustomLogger.logger


class EntrataResponseGenerator:
    
    def generate_availability_response(self, model_response, property_response, service_payload):
        '''
        Method to generate the entrata availability response
        '''
        property_id = model_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.PROPERTIES.capitalize()][EntrataConstants.PROPERTY.capitalize()][0][self.capitalize(EntrataConstants.PROPERTYID)]
        property_name = model_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.PROPERTIES.capitalize()][EntrataConstants.PROPERTY.capitalize()][0][EntrataConstants.MARKETINGNAME]
        property_response = property_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][EntrataConstants.PHYSICALPROPERTY][EntrataConstants.PROPERTY.capitalize()]
        property_obj = self.create_property_obj(property_response)
        self.create_model_obj(model_response, property_obj, property_id, property_name)
        self.create_unit_obj(model_response, property_obj, property_name, service_payload)
        units_response = UnitResponse(communities=[property_obj],prop_dict={})
        delattr(property_obj, EntrataConstants.MODELS_DICT)
        delattr(units_response, EntrataConstants.PROP_DICT)
        return units_response

    def create_unit_obj(self, unit_response, property_obj, property_name, service_payload):
        '''
        Method to create units object from input and compute their availability and pricing stats
        '''
        units = \
            set(unit_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][
                EntrataConstants.ILS_UNITS][EntrataConstants.UNIT.capitalize()].keys())

        for unit_number in units:
            
            unit = \
                unit_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT
                    ][EntrataConstants.ILS_UNITS][EntrataConstants.UNIT.capitalize()][str(unit_number)]
            
            model = \
                property_obj.models_dict.get(unit[EntrataConstants.ATTRIBUTES][EntrataConstants.FLOORPLANNAME])
            
            web_visible = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.WEBVISIBLE]
            # create unit object
            unit_obj = Unit()
            qunit_obj = QUnit()
            unit_obj.community_id = \
                unit[EntrataConstants.ATTRIBUTES][self.capitalize(EntrataConstants.PROPERTYID)]
            
            unit_obj.building = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.BUILDINGNAME]
            unit_obj.floor = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.FLOORPLANNAME]
            unit_obj.unit_id = str(unit[EntrataConstants.ATTRIBUTES][EntrataConstants.PROPERTYUNITID])
            unit_obj.unit_number = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.UNITNUMBER]
            unit_obj.unit_type_name = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.FLOORPLANID]
            unit_obj.unit_type_desc = unit[EntrataConstants.ATTRIBUTES][EntrataConstants.FLOORPLANNAME]
            unit_obj.beds = model.beds
            unit_obj.baths = model.baths
            unit_obj.market_rent = Convert.round_to(float(unit[EntrataConstants.RENT][EntrataConstants.ATTRIBUTES][EntrataConstants.MINRENT]))
            unit_obj.sqft_min = Convert.round_to(float(0))
            unit_obj.sqft_max = Convert.round_to(float(0))
            unit_obj.available_date = \
                unit[EntrataConstants.ATTRIBUTES].get(EntrataConstants.AVAILABLEON) and \
                    unit[EntrataConstants.ATTRIBUTES][EntrataConstants.AVAILABLEON] or ""
            # Checking whether the given unit is available
            unit_obj.available_boolean = \
                unit[EntrataConstants.ATTRIBUTES][EntrataConstants.AVAILABILITY
                    ] == EntrataConstants.AVAILABLE and True or False
            # populating qavailable field
            qunit_obj.qavailable_object = AvailableUnits()
            qunit_obj.qavailable_object.qUnitVisible = ConditionGenerator.generate_condition(web_visible, "in", PartnerConstants.ENTRATA.upper())
            qunit_obj.qavailable_object.qUnitVacatedDate = unit[EntrataConstants.ATTRIBUTES].get(EntrataConstants.AVAILABLEON) and unit[EntrataConstants.ATTRIBUTES][EntrataConstants.AVAILABLEON] or None
            qunit_obj.qavailable_object.qReadyToShowDate = unit[EntrataConstants.ATTRIBUTES].get(EntrataConstants.MAKE_READY_DATE) and unit[EntrataConstants.ATTRIBUTES][EntrataConstants.MAKE_READY_DATE] or None
            model.units.append(unit_obj)
            model.qunits.append(qunit_obj)
        logging.info("unit_obj: {}".format(model.units))

    def create_model_obj(self, model_response, property_obj, property_id, property_name):
        '''
        Method to create Model obj using unit obj and input data
        '''
        models_dict = {}

        for i in model_response[EntrataConstants.RESPONSE][EntrataConstants.RESULT
                    ][EntrataConstants.PROPERTIES.capitalize()][EntrataConstants.PROPERTY.capitalize()
                    ][0][EntrataConstants.FLOORPLANS][EntrataConstants.FLOORPLAN]:
           
            model_obj = UnitType()
            model_obj.community_id = property_id
            model_obj.unit_type_name = i[EntrataConstants.IDENTIFICATION][EntrataConstants.IDVALUE]
            model_obj.unit_type_desc = i[EntrataConstants.NAME]
            
            model_obj.beds = \
                Convert.round_to(float(i[EntrataConstants.ROOM][0][EntrataConstants.COUNT])) if i[EntrataConstants.ROOM
                    ][0][EntrataConstants.COMMENT] == EntrataConstants.BEDROOM else 0.0
            
            model_obj.baths = \
                Convert.round_to(float(i[EntrataConstants.ROOM][1][EntrataConstants.COUNT])) if i[EntrataConstants.ROOM
                    ][1][EntrataConstants.COMMENT] == EntrataConstants.BATHROOM else 0.0
            
            model_obj.total_units = i[EntrataConstants.UNITCOUNT]
            model_obj.sqft_model_base = Convert.round_to(float(0))
            model_obj.sqft_info = SquareFeetInfo()
            
            model_obj.sqft_info.sqft_min_all = \
                int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN])
            
            model_obj.sqft_info.sqft_max_all = \
                int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MAX])
            
            model_obj.sqft_info.sqft_min_report = \
                int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN]
                    ) if int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN]
                    ) > 0 else model_obj.sqft_model_base
            
            model_obj.sqft_info.sqft_max_report = \
                int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MAX]
                    ) if int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MAX]
                    ) > 0 else model_obj.sqft_model_base
            
            model_obj.sqft_range = \
                int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN]
                    )if int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN]
                    ) == int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MAX]
                    ) else int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MIN]
                    ) + "-" + int(i[EntrataConstants.SQUAREFEET][EntrataConstants.ATTRIBUTES][EntrataConstants.MAX])
            
            model_obj.urls = URLS()
            model_obj.urls.floorplan = i[EntrataConstants.NAME]
            
            model_obj.urls.floorplan_alt_text = \
                i[EntrataConstants.COMMENT] if EntrataConstants.COMMENT in i else i[EntrataConstants.NAME]
            
            models_dict[model_obj.unit_type_desc] = model_obj
            property_obj.unit_types.append(model_obj)
        property_obj.models_dict = models_dict
        logging.info("propert_obj_inside_model: {}".format(property_obj))

    def create_property_obj(self, property_response):
        '''
        Method to create property object using property response
        '''
        property_obj = Community()
        property_obj.provenance = [PartnerConstants.ENTRATA] 
        property_obj.address = property_response[0][EntrataConstants.ADDRESS][EntrataConstants.ADDRESS]
        property_obj.city = property_response[0][EntrataConstants.ADDRESS][EntrataConstants.CITY]
        property_obj.state_province = property_response[0][EntrataConstants.ADDRESS][EntrataConstants.STATE]
        property_obj.postal = property_response[0][EntrataConstants.ADDRESS][EntrataConstants.POSTALCODE]
        property_obj.email = property_response[0][EntrataConstants.ADDRESS][EntrataConstants.EMAILL]
        property_obj.source_system = PartnerConstants.ENTRATA
        return property_obj

    def capitalize(self, str):
        return str[0].upper() + str[1:]
import datetime, re
import os

import xml.etree.ElementTree as etree

from UnitShared.Model.UnitResponseV2 import UnitResponse, Community, UnitType, URLS, Unit, QUnit
from ResmanShared.Utilities.ResmanConstants import ResmanConstants
from VendorShared.Utilities.VendorConstants import PartnerConstants
from Utils.ConditionGenerator import ConditionGenerator
from UnitShared.Utils.Utils import AvailableUnits
from Utils import CustomLogger

logging = CustomLogger.logger


class ResmanUnitResponse:
    '''
    Class to generate Resman Unit response output taking in Resman api xml response
    '''
    logging.info("Availability Respose Generate")
    def generate_availability_response(self, xml, service_payload):
        xml = etree.fromstring(xml)
        xpath_prefix = "Response/PhysicalProperty/Property/"
        prop_dict = {}
        for prop in xml.findall("Response/PhysicalProperty/Property"):
            prop_obj = create_property(xml,xpath_prefix)
            model = create_models(xml, xpath_prefix, prop_obj, prop.attrib['IDValue'])
            units = create_units(xml, xpath_prefix, model, service_payload)
            delattr(prop_obj, 'models_dict')
            units_response = UnitResponse(**{"communities": [prop_obj], "prop_dict": prop_dict })
            delattr(units_response, 'prop_dict')
        return units_response


def create_property(xml, xpath_prefix):
    '''
        This Method is used to generate Property Object
    '''
    logging.debug("Create Property: Resman")
    property_name = xml.findall(xpath_prefix + "PropertyID/MarketingName")[0].text
    address = xml.findall(xpath_prefix + "PropertyID/Address/AddressLine1")[0].text
    if xml.findall(xpath_prefix + "PropertyID/Address/AddressLine2"):
        address2 = xml.findall(xpath_prefix + "PropertyID/Address/AddressLine2")[0].text
    else:
        address2 = ""
    city = xml.findall(xpath_prefix + "PropertyID/Address/City")[0].text
    state = xml.findall(xpath_prefix + "PropertyID/Address/State")[0].text
    postal = xml.findall(xpath_prefix + "PropertyID/Address/PostalCode")[0].text
    email = xml.findall(xpath_prefix + "PropertyID/Email")[0].text
    phone = xml.findall(xpath_prefix + "PropertyID/Phone[@PhoneType='personal']/PhoneNumber")[0].text
    speed_dial = xml.findall(xpath_prefix + "PropertyID/Phone[@PhoneType='personal']/PhoneNumber")[0].text
    fax = xml.findall(xpath_prefix + "PropertyID/Phone[@PhoneType='fax']/PhoneNumber")[0].text

    property = Community(**{"provenance": [PartnerConstants.RESMAN, os.getenv("Environment", "")], "address": address,"address2": address2,
                        "city": city,"state_province": state,"postal": postal,"email": email,
                        "phone": phone,"speed_dial": speed_dial,"fax": fax,"source_system": ResmanConstants.SOURCESYSTEM,"models_dict": {}
        })
   
    return property



def create_models(xml, xpath_prefix, property, property_id):
    '''
        This Method is used to generate Model Object
    '''
    logging.debug("Create Models: Resman")
    model_dict = {}

    property_id = property_id
    website = xml.findall(xpath_prefix + "PropertyID/WebSite")[0].text
    for f in xml.findall(xpath_prefix + ResmanConstants.FLOORPLAN):
        model_type = f.attrib["IDValue"]
        model_name = f.findall("Name")[0].text
        beds = float(f.findall("Room[@RoomType='Bedroom']/Count")[0].text)
        baths = float(f.findall("Room[@RoomType='Bathroom']/Count")[0].text)
        available = int(f.findall("UnitsAvailable")[0].text)
        total_units = f.findall("UnitCount") and int(f.findall("UnitCount")[0].text) or None
        photos = []
        virtual_tour = ""
        for file in f.findall("File"):
            if file.findall("FileType")[0].text == ResmanConstants.FLOORPLAN:
                floorplan = file.findall("Src")[0].text
            elif file.findall("FileType")[0].text == "Video":
                iframe_markup = file.findall("Src")[0].text
                virtual_tour = re.findall(r'src="(.+?)"', iframe_markup)[0]
            elif file.findall("FileType")[0].text == "Photo":
                photos.append(file.findall("Src")[0].text)

        sqft_model_base = float(f.findall("SquareFeet")[0].attrib["Avg"])
        floorplan_alt_text = f.findall("Comment") and f.findall("Comment")[0].text or None
        urls = URLS(**{
            "files": photos,
            "website": website,
            "virtual_tour_url":virtual_tour,
            "virtual_tour": virtual_tour,
            "floorplan": floorplan,
            "floorplan_alt_text": floorplan_alt_text
        })
        model_obj = UnitType(**{"community_id": property_id, 
                                "unit_type_name": model_type, 
                                "unit_type_desc": model_name,
                                "beds": beds, 
                                "baths": baths, 
                                "total_units": total_units, 
                                "total_available_units": available,
                                "urls": urls,
                                "sqft_model_base": sqft_model_base,
                                "models_dict": {}, 
                                "available_units": [], 
                                "unavailable_units": []
                        })

        property.unit_types.append(model_obj)
        if model_name in model_dict.keys():
            model_dict[model_name].append(model_obj)
        else:
            model_dict[model_name] = [model_obj]   
    return model_dict


def create_units(xml, xpath_prefix, models, service_payload):
    '''
        This Method is used to generate Unit Object
    '''
    logging.debug("Create Units: Resman")
    unit_floor_plan_min_value = {}
    unit_floor_plan_min_avl_value = {}
    sqft_all_min_max_result_dict = {}
    sqft_avl_min_max_result_dict = {}
    unit_market_rent_all_result = {}
    unit_market_rent_avail_result = {}
    effective_amount = None
    min_all_value = None
    max_all_value = None
    max_avl_value = None
    min_avl_value = None
    for model_name, model_obj in models.items():
        units, qunits = [], []
        unit_available_date = []
        for i in xml.findall(xpath_prefix + "ILS_Unit"):
            if i.findall("Units/Unit/FloorplanName")[0].text == model_name:
                unit_id = i.findall("Units/Unit/MarketingName")[0].text
                floor = int(i.findall("FloorLevel")[0].text)
                unit_number = i.findall("Units/Unit/MarketingName")[0].text
                sqft = int(i.findall("Units/Unit/MaxSquareFeet")[0].text)
                floorplan = i.findall("Units/Unit/FloorplanName")[0].text
                beds = i.findall("Units/Unit/UnitBedrooms")[0].text
                baths = i.findall("Units/Unit/UnitBathrooms")[0].text
                building = i.findall("Units/Unit/BuildingName") and i.findall("Units/Unit/BuildingName")[0].text or None
                is_available = i.findall("Units/Unit/UnitLeasedStatus") and i.findall("Units/Unit/UnitLeasedStatus")[0].text or None
                sqft_min = i.findall("Units/Unit/MinSquareFeet")[0].text
                sqft_max = i.findall("Units/Unit/MaxSquareFeet")[0].text
                unit_status = f"{i.findall('Units/Unit/UnitOccupancyStatus')[0].text} - {i.findall('Units/Unit/UnitLeasedStatus')[0].text}"
                if is_available == 'available':
                    available_boolean = 'true'
                    available_date = str(datetime.date(int(i.findall("Availability/MadeReadyDate")[0].attrib["Year"]),
                                        int(i.findall("Availability/MadeReadyDate")[0].attrib["Month"]),
                                        int(i.findall("Availability/MadeReadyDate")[0].attrib["Day"])))
                else:
                    available_boolean = 'false'
                    available_date = ""

                for r in i.findall("Pricing/MITS-OfferTerm"):
                    effective_amount = min_value(effective_amount, float(r.findall("EffectiveRent")[0].text))

                if available_date:
                    unit_available_date.append(available_date)


                effective_min_rent_amount = None
                if i.findall("EffectiveRent"):
                    effective_min_rent_amount = float(i.findall("EffectiveRent")[0].attrib['Min']) if 'Min' in i.findall("EffectiveRent")[0].attrib else None

                if effective_min_rent_amount is None:
                    effective_min_rent_amount = effective_amount
                model_type = i.findall("Units/Unit/UnitType")[0].text
                min_rent_value_unit = effective_min_rent_amount
               
                if i.findall("Units/Unit/UnitLeasedStatus")[0].text in ['available', 'on_notice']:
                    if unit_floor_plan_min_value.get(floorplan) is not None:
                        min_rent_value_unit = min_value(min_rent_value_unit, unit_floor_plan_min_value.get(floorplan))
                        unit_floor_plan_min_avl_value[floorplan] = min_rent_value_unit
                    else:
                        unit_floor_plan_min_avl_value[floorplan] = min_rent_value_unit
                else:
                    if unit_floor_plan_min_value.get(floorplan) is not None:
                        min_rent_value_unit = min_value(min_rent_value_unit, unit_floor_plan_min_value.get(floorplan))
                    else:
                        unit_floor_plan_min_value[floorplan] = min_rent_value_unit

                max_sqft = "Units/Unit/MaxSquareFeet"
                min_sqft = "Units/Unit/MinSquareFeet"
                available_status = "Units/Unit/UnitLeasedStatus"
                sqft_all_min_max = get_min_max_sqft(i, sqft_all_min_max_result_dict, floorplan, max_sqft, min_sqft, min_value = min_all_value, max_value = max_all_value)
                min_all_value = sqft_all_min_max[floorplan][0]
                max_all_value = sqft_all_min_max[floorplan][1]

                if i.findall(available_status)[0].text in ['available', 'on_notice']:
                    sqft_avl_min_max = get_min_max_sqft(i, sqft_avl_min_max_result_dict, floorplan, max_sqft, min_sqft, min_value = min_avl_value, max_value = max_avl_value)
                    min_avl_value = sqft_avl_min_max[floorplan][0]
                    max_avl_value = sqft_avl_min_max[floorplan][1]

                unit_market_rent_all_result = get_min_rent(unit_market_rent_all_result, floorplan, unit_floor_plan_min_value)

                if i.findall(available_status)[0].text in ['available', 'on_notice']:
                    unit_market_rent_avail_result = get_min_rent(unit_market_rent_avail_result, floorplan, unit_floor_plan_min_avl_value)
                
                UnitEconomicStatus = i.findall("Units/Unit/UnitEconomicStatus") and i.findall("Units/Unit/UnitEconomicStatus")[0].text or ""
                if i.findall("Availability/VacateDate"):
                    vacate_date = str(datetime.date( int(i.findall("Availability/VacateDate")[0].attrib["Year"]),
                                                    int(i.findall("Availability/VacateDate")[0].attrib["Month"]),
                                                    int(i.findall("Availability/VacateDate")[0].attrib["Day"]) )
                    )
                else:
                    vacate_date = ""
                units.append(Unit(**{
                        "community_id": model_obj[0].community_id, 
                        "unit_id": unit_id, 
                        "unit_number": unit_number, 
                        "available_boolean": available_boolean, 
                        "unit_status": unit_status,
                        "available_date": available_date, 
                        "unit_type_name": unit_number, 
                        "unit_type_desc": floorplan, 
                        "beds": beds, 
                        "baths": baths,
                        "market_rent": min_rent_value_unit,
                        "sqft_min": sqft_min, 
                        "sqft_max": sqft_max
                        } ))
                qunits.append(QUnit(**{
                   "qavailable_object": AvailableUnits(
                        qReadyToShowDate=i.findall("Availability/MadeReadyDate") and i.findall("Availability/MadeReadyDate")[0].text or "",
                        qUnitVacatedDate = vacate_date,
                        qUnitVisible= ConditionGenerator.generate_condition(UnitEconomicStatus, "in", PartnerConstants.RESMAN.upper()))
                    }
                ))
                model_obj[0].units = units
                model_obj[0].qunits = qunits


def min_value(*args):
    '''
        This Method is used to get the min value
    '''
    values = []
    for arg in args:
        if arg is not None:
            values.append(float(arg))
    return min(values) if len(values) > 0 else None

    
    
def get_min_max_sqft(xml, result_dict, floorplan, max_field, 
                        min_field, min_value = None, max_value = None):
    '''
        This Method is used to get the min and max square feet value
    '''
    
    floorplans = floorplan
    max_value = max_field and int(xml.findall(max_field)[0].text) or None
    min_value = min_field and int(xml.findall(min_field)[0].text) or None
    if floorplans in result_dict:
        min_value = result_dict[floorplans][0] 
        max_value = result_dict[floorplans][1] 
        max_value = int(xml.findall(max_field)[0].text) if max_value < int(xml.findall(max_field)[0].text) else max_value
        min_value = int(xml.findall(min_field)[0].text) if min_value > int(xml.findall(min_field)[0].text) else min_value

    result_dict[floorplans] = min_value, max_value
    return result_dict

def get_min_rent(result_dict, floorplan, input_dict):
    '''
        This Method is used to get the min rent
    '''
    
    min_value = floorplan in input_dict and input_dict[floorplan] or None
    if floorplan in result_dict and result_dict[floorplan] is not None:
        min_value = result_dict[floorplan]
        min_value = input_dict[floorplan]  if floorplan in input_dict and input_dict[floorplan] < min_value  else min_value
    result_dict[floorplan] = min_value
    
    return result_dict


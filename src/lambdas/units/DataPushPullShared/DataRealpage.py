import os
import datetime, json
from Utils.Constants.RealpageConstants import RealpageConstants
import suds

class DataRealpage:
        
    def get_unit_availability(self, ips):
        errors = []
        wsdl = RealpageConstants.WSDL_URL
        client = suds.client.Client(wsdl)
        _auth = client.factory.create(RealpageConstants.AUTHDTO)
        _auth.pmcid = os.environ[RealpageConstants.PMCID]
        _auth.siteid = os.environ[RealpageConstants.SITEID]
        _auth.licensekey = os.environ[RealpageConstants.LICENSE_KEY]

  
        date_needed = datetime.date.today() + datetime.timedelta(days=30)
        listcriterion = client.factory.create('ArrayOfListCriterion')
        
        date_criterion = client.factory.create(RealpageConstants.LIST_CRITERION)
        date_criterion.name = RealpageConstants.DATE_NEEDED
        date_criterion.singlevalue = date_needed.strftime("%Y-%m-%d")
        
        limit_criterion = client.factory.create(RealpageConstants.LIST_CRITERION)
        limit_criterion.name = RealpageConstants.LIMIT_RESULTS
        limit_criterion.singlevalue = False
        
        listcriterion.ListCriterion.append(date_criterion)
        listcriterion.ListCriterion.append(limit_criterion)
        
        response = client.service.getunitlist(auth=_auth, listCriteria=listcriterion)
       
        property, models, units = self.translateRealPage(response[RealpageConstants.GET_UNIT_LIST][RealpageConstants.UNIT_OBJECTS][RealpageConstants.UNIT_OBJECT], ips[RealpageConstants.PLATFORMDATA][RealpageConstants.FOREIGN_COMMUNITY_ID])
        
        return property, models, units, errors
    
    def translateRealPage(self, vals, foreign_community_id=None):
        models = []
        units = []
        property_id = None
        property = {}
        model_type_list = []
        for input_dict in vals:
            if not property_id:
                property_id = input_dict[RealpageConstants.PROPERTY_NUMBER_ID]
                property = { 
                    "name": input_dict[RealpageConstants.PROPERTY_NUMBER_ID], 
                    "address": input_dict[RealpageConstants.ADDRESS][RealpageConstants.ADDRESS1], 
                    "address2": None, 
                    "city": input_dict[RealpageConstants.ADDRESS][RealpageConstants.CITY_NAME], 
                    "state": input_dict[RealpageConstants.ADDRESS][RealpageConstants.STATE], 
                    "postal": input_dict[RealpageConstants.ADDRESS][RealpageConstants.ZIP], 
                    "email": None, 
                    "phone": None, 
                    "speed_dial": None, 
                    "fax": None,
                    "source_system": RealpageConstants.PARTNER_NAME
                }
            model_type = input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE]
            if model_type not in model_type_list:
                model_type_list.append(input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE])
                models.append({
                            "model_type": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE],
                            "beds": int(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BEDROOMS]), 
                            "baths": int(float(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BATHROOMS])),
                            "floorplan": None,
                            "virtual_tour": None,
                            "photos": [], 
                            "sqft": int(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT]),
                            "floorplan_alt_text": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_NAME],
                            "sqft_range": input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT],
                            "unit_type_desc": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_NAME],
                            "unit_type_name": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE],
                            "website": None,
                            "virtual_tour_url": None,
                            "sqft_model_base": input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT],
                            "property_name": input_dict[RealpageConstants.PROPERTY_NUMBER_ID],
                            "foreign_community_id": foreign_community_id
                        })
            
            units.append({ 
                    "floor": int(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.FLOOR_NUMBER]), 
                    "unit_number": input_dict[RealpageConstants.ADDRESS][RealpageConstants.UNIT_NUMBER], 
                    "sqft": int(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.GROSS_SQFT_COUNT]), 
                    "beds": int(float(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BEDROOMS])),
                    "baths": int(float(input_dict[RealpageConstants.UNIT_DETAILS][RealpageConstants.BATHROOMS])),
                    "rent_amount": int(float(input_dict[RealpageConstants.EFFECTIVE_RENT])),
                    "market_rent_amount": int(float(input_dict[RealpageConstants.FLOOR_PLAN_MARKET_RENT])),
                    "available_date": datetime.datetime.strptime(input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.MADE_READY_DATE], "%m/%d/%Y").strftime("%Y-%m-%d"),
                    "unit_type_name": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE],
                    "model_type": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_CODE],
                    "available": (1 if input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.AVAILABLEBIT] == "true" else 0),
                    "available_boolean":("true" if input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.AVAILABLEBIT] == "true" else "false"),
                    "building":input_dict[RealpageConstants.ADDRESS][RealpageConstants.BUILDING_ID],
                    "is_available": (1 if input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.AVAILABLEBIT] == "true" else 0),
                    "market_rent": int(float(input_dict[RealpageConstants.EFFECTIVE_RENT])),
                    "property_id":input_dict[RealpageConstants.PROPERTY_NUMBER_ID],
                    "property_name":input_dict[RealpageConstants.PROPERTY_NUMBER_ID],
                    "unit_id": int(input_dict[RealpageConstants.ADDRESS][RealpageConstants.UNIT_ID]),
                    "unit_status": ("vacant - available" if input_dict[RealpageConstants.AVAILABILITY][RealpageConstants.AVAILABLEBIT] == "true" else "un-available"),
                    "unit_type_desc": input_dict[RealpageConstants.FLOOR_PLAN][RealpageConstants.FLOOR_PLAN_NAME]
                })

        for model in models:
            rent = []
            sqft_min_max = []
            unit_date_avail = []
            for unit in units:
                if unit['unit_type_name'] == model['model_type']:
                    rent.append(unit['rent_amount'])
                    sqft_min_max.append(unit['sqft'])
                    sqft_min_max.append(unit['sqft'])
                    unit_date_avail.append(unit['available_date'])
            model['market_rent'] = int(float(min(rent)))
            model['available'] = model['total_units'] = len(rent)
            model['sqft_max_all'] = model['sqft_max_avail'] =  int(max(sqft_min_max))
            model['sqft_min_all'] = model['sqft_min_avail'] = int(min(sqft_min_max))
            model['sqft_min_report'] = model['sqft_min_all'] and int(model['sqft_min_all']) or int(model['sqft'])
            model['sqft_max_report'] = model['sqft_max_all'] and int(model['sqft_max_all']) or int(model['sqft'])
            model['unit_market_rent_all'] = int(float(min(rent)))
            model['unit_market_rent_avail'] = int(float(min(rent)))
            model['sqft_model_base'] = int(min(sqft_min_max))
            model['unit_type_first_avail'] = min(unit_date_avail)

        return property, models, units
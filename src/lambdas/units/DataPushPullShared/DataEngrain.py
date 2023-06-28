import requests
from Utils.Config.Config import config
from Utils.Constants.EngrainConstants import EngrainConstants
class DataEngrain:

    def get_unit_availability(self, ips):
        asset_id = ips[EngrainConstants.PLATFORM_DATA]["asset_id"]
        api_key = ips[EngrainConstants.PLATFORM_DATA]["api_key"]
        engrain_host = config["Engrain_host"]

        url_floorplans = f"{engrain_host}{EngrainConstants.PATH}{asset_id}/multifamily/floor-plans"
        headers = {'API-Key': api_key}

        floorplans = requests.get(url_floorplans, headers=headers)
        floorplans_data = floorplans.json()

        process_id = self.getPricingProcessId(asset_id)
        url_units = f"{engrain_host}{EngrainConstants.PATH}{asset_id}/multifamily/pricing/{process_id}/units"
        units_pricing = requests.get(url_units, headers=headers)
        units_pricing_data = units_pricing.json()
        

        url_assets = f"{engrain_host}{EngrainConstants.PATH}{asset_id}"
        asset = requests.get(url_assets, headers=headers)
        asset_data = asset.json()

        url_units = f"{engrain_host}{EngrainConstants.PATH}{asset_id}/multifamily/units"
        units_response = requests.get(url_units, headers=headers)
        units_response_data = units_response.json()

        units_fixed = []
        for unit in units_response_data[EngrainConstants.DATA]:
            units_fixed.append(
                self.transform_units_json(unit, units_pricing_data[EngrainConstants.DATA]))

        models = self.getEngrainModels(units_response_data[EngrainConstants.DATA],
                                    floorplans_data[EngrainConstants.DATA],units_pricing_data[EngrainConstants.DATA])
        return asset_data, models, units_fixed, []
    
    def get_price(self, prices, unit_number):
        for price in prices:
            if price[EngrainConstants.UNIT_NUMBER] == unit_number:
                return price["price"]

        return None

    def transform_units_json(self, input_json, prices):
        data = input_json

        transformed_data = {
        "floor": int(data.get(EngrainConstants.FLOOR_ID, 0)),
        "unit_number": str(data.get(EngrainConstants.UNIT_NUMBER, "")),
        "sqft": int(data.get(EngrainConstants.AREA, 0)),
        "beds": int(data.get(EngrainConstants.BEDS, 0)),
        "baths": int(data.get(EngrainConstants.BATHS, 0)),
        "rent_amount": self.get_price(prices, str(data.get(EngrainConstants.UNIT_NUMBER, ""))),
        "market_rent_amount": float(data.get(EngrainConstants.MARKET_RENT_AMOUNT, 0.0)),
        "available_date": data.get(EngrainConstants.AVAILABLE_DATE, ""),
        "unit_type_name": data.get(EngrainConstants.UNIT_TYPE_NAME, ""),
        "model_type": data.get(EngrainConstants.MODEL_TYPE, ""),
        "available": int(data.get(EngrainConstants.AVAILABLE, 0)),
        "available_boolean": str(data.get(EngrainConstants.AVAILABLE_BOOLEAN, "false")),
        "building": data.get(EngrainConstants.BUILDING, ""),
        "is_available": int(data.get(EngrainConstants.IS_AVAILABLE, 0)),
        "market_rent": int(data.get(EngrainConstants.MARKET_RENT, 0)),
        "property_id": data.get(EngrainConstants.PROPERTY_ID, ""),
        "property_name": data.get(EngrainConstants.PROPERTY_NAME, ""),
        "unit_id": int(data.get(EngrainConstants.ID, 0)),
        "unit_status": data.get(EngrainConstants.UNIT_STATUS, ""),
        "unit_type_desc": data.get(EngrainConstants.UNIT_TYPE_DESC, "")
        }

        return transformed_data

    def getEngrainModels(self, units, floors, units_pricing_data):
        models = []

        for floor in floors:
            model = {
                "model_type": floor["name"],
                "beds": floor["bedroom_count"],
                "baths": floor["bathroom_count"],
                "market_rent": self.getMaxPrice(floor["id"], units,
                                                units_pricing_data),
                "available": 0,
                "floorplan": floor["image_url"],
                "virtual_tour": "",
                "photos": [],
                "sqft": 0,
                "floorplan_alt_text": "",
                "sqft_max_all": 0,
                "sqft_min_all": 0,
                "sqft_max_avail": 0,
                "sqft_min_avail": 0,
                "sqft_min_report": 0,
                "sqft_max_report": 0,
                "sqft_range": "0",
                "total_units": 0,
                "unit_market_rent_all": 0,
                "unit_market_rent_avail": 0,
                "unit_type_desc": "",
                "unit_type_first_avail": "",
                "unit_type_name": floor["name"],
                "website": "",
                "virtual_tour_url": "",
                "sqft_model_base": 0,
                "property_name": "Engrain",
                "foreign_community_id": ""
            }
            models.append(model)

        return models

    def getMaxPrice(self, floor_plan_id, units, units_pricing_data):
        prices = []
        for unit in units:
            if floor_plan_id == unit[EngrainConstants.FLOORPLAN_ID] and self.get_price(
                units_pricing_data, unit[EngrainConstants.UNIT_NUMBER]) is not None:

                prices.append(
                int(self.get_price(units_pricing_data, unit[EngrainConstants.UNIT_NUMBER])))
        
            max_price = max(prices) if len(prices) > 0 else 0
        return (str(max_price))

    def getPricingProcessId(self, asset_id):
        engrain_host = config["Engrain_host"]
        api_key = config["Engrain_api_key"]
        url = f'{engrain_host}{asset_id}/multifamily/pricing'
        headers = {'API-Key': {api_key}}
        process_id = 0
        processes = requests.get(url, headers=headers)
        data = processes.json()

        for price in data[EngrainConstants.DATA]:
          if price["type"] == "push":
                process_id = price["id"]
                break

    
        return process_id
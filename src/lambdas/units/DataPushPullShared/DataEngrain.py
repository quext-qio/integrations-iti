import requests

class DataEngrain:

    def get_unit_availability(self, ips):
        asset_id = ips["platformData"]["asset_id"]
        api_key = ips["platformData"]["api_key"]

        url_floorplans = f"https://api.sightmap.com/v1/assets/{asset_id}/multifamily/floor-plans"
        headers = {'API-Key': api_key}

        floorplans = requests.get(url_floorplans, headers=headers)
        floorplans_data = floorplans.json()

        process_id = self.getPricingProcessId(asset_id)
        url_units = f"https://api.sightmap.com/v1/assets/{asset_id}/multifamily/pricing/{process_id}/units"
        units_pricing = requests.get(url_units, headers=headers)
        units_pricing_data = units_pricing.json()
        

        url_assets = f"https://api.sightmap.com/v1/assets/{asset_id}"
        asset = requests.get(url_assets, headers=headers)
        asset_data = asset.json()

        url_units = f"https://api.sightmap.com/v1/assets/{asset_id}/multifamily/units"
        units_response = requests.get(url_units, headers=headers)
        units_response_data = units_response.json()

        units_fixed = []
        for unit in units_response_data["data"]:
            units_fixed.append(
                self.transform_units_json(unit, units_pricing_data["data"]))

        models = self.getEngrainModels(units_response_data["data"],
                                    floorplans_data["data"],units_pricing_data["data"])
        return asset_data, models, units_fixed, 200
    
    def get_price(self, prices, unit_number):
        for price in prices:
            if price["unit_number"] == unit_number:
                return price["price"]

        return None

    def transform_units_json(self, input_json, prices):
        data = input_json

        transformed_data = {
        "floor": int(data.get("floor_id", 0)),
        "unit_number": str(data.get("unit_number", "")),
        "sqft": int(data.get("area", 0)),
        "beds": int(data.get("beds", 0)),
        "baths": int(data.get("baths", 0)),
        "rent_amount": self.get_price(prices, str(data.get("unit_number", ""))),
        "market_rent_amount": float(data.get("market_rent_amount", 0.0)),
        "available_date": data.get("available_date", ""),
        "unit_type_name": data.get("unit_type_name", ""),
        "model_type": data.get("model_type", ""),
        "available": int(data.get("available", 0)),
        "available_boolean": str(data.get("available_boolean", "false")),
        "building": data.get("building", ""),
        "is_available": int(data.get("is_available", 0)),
        "market_rent": int(data.get("market_rent", 0)),
        "property_id": data.get("property_id", ""),
        "property_name": data.get("property_name", ""),
        "unit_id": int(data.get("id", 0)),
        "unit_status": data.get("unit_status", ""),
        "unit_type_desc": data.get("unit_type_desc", "")
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
            if floor_plan_id == unit["floor_plan_id"] and self.get_price(
                units_pricing_data, unit["unit_number"]) is not None:

                prices.append(
                int(self.get_price(units_pricing_data, unit["unit_number"])))
        
            max_price = max(prices) if len(prices) > 0 else 0
        return (str(max_price))

    def getPricingProcessId(asset_id):
        url = f'https://api.sightmap.com/v1/assets/{asset_id}/multifamily/pricing'
        headers = {'API-Key': 'QOZgAsIsMgOwxLTDV4selhYrhePKLoGz'}
        process_id = 0
        processes = requests.get(url, headers=headers)
        data = processes.json()

        for price in data["data"]:
          if price["type"] == "push":
                process_id = price["id"]
                break

    
        return process_id
from Utils.Constants.RealpageConstants import RealpageConstants
from urllib.parse import urlencode
import xml.etree.ElementTree as etree
import os
import datetime, re
import requests


class DataResman:

    def get_unit_availability(self, ips, event):
   
        code = 200
        errors = []

        # These get replaced into the url template.
        _params = { 
            "interface": "MITS",
            "method": "GetMarketing4_0",          
        }
        
        body = {}
        if code:
            body = { 
                "PropertyID": ips["platformData"]["foreign_community_id"],
                "AccountID": ips["platformData"]["foreign_customer_id"],
                "IntegrationPartnerID": "20422",
                "ApiKey": "01mu8cUPjJUeTZtaPwyFGAhAtou70859"
            }
        else:
            #Depending on the application hitting this endpoint, we may need to send different credentials, so look those up.
            credentials, status = AccessUtils.externalCredentials(self.wsgi_environ, self.logger, "ResMan")
            if status != "good":
                errors.append({ "status": "error", "message": status })
                response = { "data": { "provenance": ["resman"] }, "errors": errors }
                return response, 500

            body = { 
                 "PropertyID": ips["platformData"]["foreign_community_id"],
                "AccountID": ips["platformData"]["foreign_customer_id"],
                "IntegrationPartnerID": "20422",
                "ApiKey": "01mu8cUPjJUeTZtaPwyFGAhAtou70859"
            }
          
        base_url = 'https://api.myresman.com'
        interface = 'MITS'
        method = 'GetMarketing4_0'
        url = f'{base_url}/{interface}/{method}'
        _body = urlencode(body, {"Content-type": "application/x-www-form-urlencoded"})
    
        # Prepare the headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Content-Length': str(len(_body))
        }
    
        # Send the HTTP POST request
        resmanChannelResponse = requests.post(url, data=_body, headers=headers)
        # json_xml = json.loads(Converter(resmanChannelResponse.text).xml_to_json())
        # return [json_xml], 200    

        xml = etree.fromstring(resmanChannelResponse.text)
        if resmanChannelResponse.status_code != 200:
            print(resmanChannelResponse.status_code)
            errors.append({ "status_code": resmanChannelResponse.status_code, 
                            "status": xml.findall('Status')[0].text, 
                            "message": xml.findall('ErrorDescription')[0].text })
            response = { "data": { "provenance": ["resman"] }, "errors": errors }
            code = 502
        elif xml.findall("ErrorDescription"):
            code = 502
            errors.append({ "status": "error", "message": xml.findall("./ErrorDescription")[0].text })
            response = { "data": { "provenance": ["resman"], }, "errors": errors }
        else:
            property, models, units = self.translateResmanXML(xml, "MITS/GetMarketing4_0", ips, event)
            response = { "data": { "provenance": ["resman"], "property": property, "models": models, "units": units }, "errors": errors }
   
        return property, models, units, code

   
    def translateResmanXML(self, xml, method, ips, event):
        
        # This isn't true Xpath 1.0, but some subset with changes. See:
        # https://docs.python.org/3/library/xml.etree.elementtree.html#xpath-support
        
        if method == "MITS/GetMarketing4_0":
            # This block extracts the "property" object from ResMan xml.
            xpath_prefix = "Response/PhysicalProperty/Property/PropertyID/"

            property_name = xml.findall(xpath_prefix + "MarketingName")[0].text
            address = xml.findall(xpath_prefix + "Address/AddressLine1")[0].text
            if xml.findall(xpath_prefix + "Address/AddressLine2"):
                address2 = xml.findall(xpath_prefix + "Address/AddressLine2")[0].text
            else:
                address2 = None
            city = xml.findall(xpath_prefix + "Address/City")[0].text
            state = xml.findall(xpath_prefix + "Address/State")[0].text
            postal = xml.findall(xpath_prefix + "Address/PostalCode")[0].text
            email = xml.findall(xpath_prefix + "Email")[0].text
            phone = xml.findall(xpath_prefix + "Phone[@PhoneType='personal']/PhoneNumber")[0].text
            speed_dial = xml.findall(xpath_prefix + "Phone[@PhoneType='personal']/PhoneNumber")[0].text
            fax = xml.findall(xpath_prefix + "Phone[@PhoneType='fax']/PhoneNumber")[0].text
            
            foreign_community_id = ips["platformData"]["foreign_community_id"] if "platformData" in ips and "foreign_community_id" in ips["platformData"] else "" 
            source_system = ips["platformData"]["platform"] if "platformData" in ips and "platform" in ips["platformData"] else "" 

            property = { 
                "name": property_name, 
                "address": address, 
                "address2": address2, 
                "city": city, 
                "state": state, 
                "postal": postal, 
                "email": email, 
                "phone": phone, 
                "speed_dial": speed_dial, 
                "fax": fax,
                "source_system": source_system
            }
            
            # This block extracts the "units" object from ResMan xml.
            units = []
            xpath_prefix = "Response/PhysicalProperty/Property/"
            unit_floor_plan_min_value = {}
            effective_amount = None
            for i in xml.findall(xpath_prefix + "ILS_Unit"):
                floor = int(i.findall("FloorLevel")[0].text)
                unit_number = i.findall("Units/Unit/MarketingName")[0].text
                sqft = int(i.findall("Units/Unit/MaxSquareFeet")[0].text)
                floorplan = i.findall("Units/Unit/FloorplanName")[0].text
                beds = float(i.findall("Units/Unit/UnitBedrooms")[0].text)
                baths = float(i.findall("Units/Unit/UnitBathrooms")[0].text)

                unit_property_name_aux = i.attrib["OrganizationName"] # property_name
                unit_type_desc_aux = f"{int(beds)}x{int(baths)}" # unit_type_desc
                building = i.findall("Units/Unit/Address")[0].findall("AddressLine1")[0].text
                market_rent = int(i.findall("Units/Unit/MarketRent")[0].text)
                unit_id = self.extract_number(i.attrib["IDValue"])
                available_boolean = "true" if i.findall("Units/Unit/UnitLeasedStatus")[0].text == "available" else "false"
                is_available = 1 if i.findall("Units/Unit/UnitLeasedStatus")[0].text == "available" else 0
                available_aux = 1 if i.findall("Units/Unit/UnitLeasedStatus")[0].text == "available" else 0 # available 
                unit_status = f"{i.findall('Units/Unit/UnitOccupancyStatus')[0].text} - {i.findall('Units/Unit/UnitLeasedStatus')[0].text}"
                property_id = xml.findall("Response/PhysicalProperty/Property")[0].attrib["IDValue"]


                for r in i.findall("Pricing/MITS-OfferTerm"):
                    effective_amount =self.min_value(effective_amount, float(r.findall("EffectiveRent")[0].text))

                market_rent_amount = float(i.findall("Units/Unit/MarketRent")[0].text)
                effective_min_rent_amount = float(i.findall("EffectiveRent")[0].attrib['Min']) if 'Min' in i.findall("EffectiveRent")[0].attrib else None
                if effective_min_rent_amount is None:
                    effective_min_rent_amount = effective_amount
                model_type = i.findall("Units/Unit/UnitType")[0].text

                if i.findall("Availability/VacateDate"):
                    vacate_date = str(datetime.date( int(i.findall("Availability/VacateDate")[0].attrib["Year"]),
                                                    int(i.findall("Availability/VacateDate")[0].attrib["Month"]),
                                                    int(i.findall("Availability/VacateDate")[0].attrib["Day"]) )
                    )
                else:
                    vacate_date = None
                min_rent_value_unit = effective_min_rent_amount
                if "available" in event and event["available"]:
                    if i.findall("Units/Unit/UnitLeasedStatus")[0].text in ['available', 'on_notice']:
                        if unit_floor_plan_min_value.get(floorplan) is not None:
                            min_rent_value_unit = self.min_value(min_rent_value_unit, unit_floor_plan_min_value.get(floorplan))
                            unit_floor_plan_min_value[floorplan] = min_rent_value_unit
                        else:
                            unit_floor_plan_min_value[floorplan] = min_rent_value_unit
                else:
                    if unit_floor_plan_min_value.get(floorplan) is not None:
                        min_rent_value_unit = self.min_value(min_rent_value_unit, unit_floor_plan_min_value.get(floorplan))
                    else:
                        unit_floor_plan_min_value[floorplan] = min_rent_value_unit
                if "available" in event and event["available"]:
                    if i.findall("Units/Unit/UnitLeasedStatus")[0].text in ['available', 'on_notice']:
                        units.append({ 
                            "floor": floor, 
                            "unit_number": unit_number, 
                            "sqft": sqft, 
                            "beds": beds, 
                            "baths": baths,
                            "rent_amount": effective_min_rent_amount, 
                            "market_rent_amount": min_rent_value_unit,
                            "available_date": vacate_date,  
                            "unit_type_name": model_type,
                            "model_type": model_type,
                            "available":available_aux,
                            "available_boolean":available_boolean,
                            "building":building,
                            "is_available":is_available,
                            "market_rent":market_rent,
                            "property_id":property_id,
                            "property_name":unit_property_name_aux,
                            "unit_id":unit_id,
                            "unit_status":unit_status,
                            "unit_type_desc":unit_type_desc_aux
                        })
                else:
                    units.append({ 
                        "floor": floor, 
                        "unit_number": unit_number, 
                        "sqft": sqft, 
                        "beds": beds, 
                        "baths": baths,
                        "rent_amount": effective_min_rent_amount, 
                        "market_rent_amount": min_rent_value_unit,
                        "available_date": vacate_date, 
                        "unit_type_name": model_type,
                        "model_type": model_type,
                        "available":available_aux,
                        "available_boolean":available_boolean,
                        "building":building,
                        "is_available":is_available,
                        "market_rent":market_rent,
                        "property_id":property_id,
                        "property_name":unit_property_name_aux,
                        "unit_id":unit_id,
                        "unit_status":unit_status,
                        "unit_type_desc":unit_type_desc_aux
                    })

            # This block extracts the "models" object from the ResMan xml.
            models = []
            for f in xml.findall(xpath_prefix + "Floorplan"):
                model_type = f.attrib["IDValue"]
                model_name = f.findall("Name")[0].text
                beds = int(f.findall("Room[@RoomType='Bedroom']/Count")[0].text)
                baths = float(f.findall("Room[@RoomType='Bathroom']/Count")[0].text)
                market_min_rent = float(f.findall("MarketRent")[0].attrib["Min"]) if 'Min' in f.findall("MarketRent")[0].attrib else None
                effective_min_rent = float(f.findall("EffectiveRent")[0].attrib["Min"]) if 'Min' in f.findall(
                    "EffectiveRent")[0].attrib else None
                available = int(f.findall("UnitsAvailable")[0].text)

                photos = []
                virtual_tour, floorplan = "", ""
                for file in f.findall("File"):
                    if file.findall("FileType")[0].text == "Floorplan":
                        floorplan = file.findall("Src")[0].text
                    elif file.findall("FileType")[0].text == "Video":
                        iframe_markup = file.findall("Src")[0].text
                        virtual_tour = re.findall(r'src="(.+?)"', iframe_markup)[0]
                    elif file.findall("FileType")[0].text == "Photo":
                        photos.append(file.findall("Src")[0].text)

                sqft = int(f.findall("SquareFeet")[0].attrib["Avg"])
                temp_min_avail_only_amount = None
                if "available" in event and event["available"]:
                    if model_name in unit_floor_plan_min_value.keys():
                        temp_min_avail_only_amount = self.min_value(unit_floor_plan_min_value.get(model_name))
                    if temp_min_avail_only_amount is None:
                        market_rent_value_reported = market_min_rent
                    else:
                        market_rent_value_reported = temp_min_avail_only_amount
                else:
                    market_rent_value_reported = market_min_rent
                
                website = xml.findall(xpath_prefix + "PropertyID")[0].findall("WebSite")[0].text
                floorplan_alt_text = f.findall("Comment")[0].text if len(f.findall("Comment")) > 0 else ""
                sqft_max_all = int(f.findall("SquareFeet")[0].attrib["Max"])
                sqft_min_all= int(f.findall("SquareFeet")[0].attrib["Min"])
                sqft_max_avail= int(f.findall("SquareFeet")[0].attrib["Min"])
                sqft_min_avail= int(f.findall("SquareFeet")[0].attrib["Max"])
                sqft_min_report= sqft_min_avail if sqft_min_avail > 0 else sqft_min_all
                sqft_max_report= sqft_max_avail if sqft_max_avail > 0 else sqft_max_all
                sqft_range= f"{sqft_min_report}" if sqft_min_report ==  sqft_max_report else f"{sqft_min_report}-{sqft_max_report}"
                total_units = int(f.findall("UnitCount")[0].text)
                unit_market_rent_all = int(f.findall("MarketRent")[0].attrib["Min"])
                unit_market_rent_avail = int(f.findall("MarketRent")[0].attrib["Max"])
                unit_type_desc = f"{beds}x{int(baths)}"
                virtual_tour = virtual_tour if virtual_tour != "" else None
                unit_type_first_avail= None if available == 0  else datetime.datetime.now().date() #TODO: Get correct date
                unit_type_name = f.attrib["IDValue"]
                virtual_tour_url = None
                sqft_model_base = sqft
                property_name_aux = f.attrib["OrganizationName"]  

                models.append({
                    "model_type": model_type, 
                    "beds": beds, 
                    "baths": baths,
                    "market_rent": market_rent_value_reported,
                    "available": available, 
                    "floorplan": floorplan, 
                    "virtual_tour": virtual_tour,
                    "photos": photos, 
                    "sqft": sqft,
                    "floorplan_alt_text": floorplan_alt_text,
                    "sqft_max_all": sqft_max_all,
                    "sqft_min_all": sqft_min_all,
                    "sqft_max_avail": sqft_max_avail,
                    "sqft_min_avail": sqft_min_avail,
                    "sqft_min_report": sqft_min_report,
                    "sqft_max_report": sqft_max_report,
                    "sqft_range": sqft_range,
                    "total_units": total_units,
                    "unit_market_rent_all": unit_market_rent_all,
                    "unit_market_rent_avail": unit_market_rent_avail,
                    "unit_type_desc": unit_type_desc,
                    "unit_type_first_avail": unit_type_first_avail,
                    "unit_type_name": unit_type_name,
                    "website": website,
                    "virtual_tour_url": virtual_tour_url,
                    "sqft_model_base": sqft_model_base,
                    "property_name": property_name_aux,
                    "foreign_community_id": foreign_community_id,
                })

        return property, models, units
    
    def min_value(self, *args):
        values = []
        for arg in args:
            if arg is not None:
                values.append(float(arg))
        return min(values) if len(values) > 0 else None
    
    def extract_number(self, input_string):
        stripped_string = ''.join(c for c in input_string if c.isdigit())

        if stripped_string:
            return int(stripped_string)
        else:
            return -1

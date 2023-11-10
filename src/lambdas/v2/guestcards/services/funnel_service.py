import json, requests, logging, os
from datetime import datetime
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.service_response import ServiceResponse
from constants.funnel_constants import *

class FunnelService(ServiceInterface):

    def get_data(self, body, ips):
          # Get credentials information
            group_id = ips["platformData"]["foreign_community_id"]
            prospect = body["guest"]
            preferences = body["guestPreference"]
            bedroooms_data = []
            available_time = []
            tour_schedule_id = ""
            tour_error = ""
            customer_id = ""
            headers = {"Authorization": f'Basic {os.environ["FUNNEL_API_KEY"]}'}
            tour_information = None
            source = body["source"].lower().replace("dh","digital human").replace("ws", "website")

            if "desiredBeds" in preferences:
                # Map string to int using [bedroom_mapping]
                for i in range(len(preferences["desiredBeds"])):
                    string_beds = preferences["desiredBeds"][i]
                    bedroooms_data.append(bedroom_mapping.get(string_beds, 0))
            bedrooms = str(max(bedroooms_data)) if len(bedroooms_data) > 0 else 0
            bedrooms = bedrooms.replace("1", "1br").replace("2","2br").replace("3", "3br").replace("4","4+br")
            comment = body["guestComment"] if "guestComment" in body else ""
            payload = {
                    "appointment":{
                        "start": "",
                        "tour_type": "guided", #TODO: Check if could be empty
                    },
                    "client":{
                        "people":[
                            {
                                "first_name":prospect["first_name"],
                                "last_name":prospect["last_name"],
                                "email": prospect["email"],
                                "phone_1": prospect.get("phone", ""),
                            }
                        ],
                        "move_in_date":preferences["moveInDate"] if "moveInDate" in preferences else "",
                        "layout": [bedrooms],
                        "price_ceiling": int(preferences["desiredRent"]) if "desiredRent" in preferences else 0,
                        "lead_source": source,
                        "bathrooms": preferences["desiredBaths"][0] if "desiredBaths" in preferences else 0,
                        "reason_for_move": preferences["moveInReason"] if "moveInReason" in preferences else "",
                        "amenities": preferences["preferredAmenities"] if "preferredAmenities" in preferences else "",
                        "notes": comment,
                    }
                }
            
            if "tourScheduleData" in body:
                        appointment_date = body["tourScheduleData"]["start"]
                        tour_requested = appointment_date
                        payload["appointment"].update({"start" :appointment_date[ :appointment_date.index("Z")]})
                        try:
                            payload["client"]["lead_source"] = source
                            params = {
                                "group_id": group_id
                            }

                            # Call outgoing of funnel
                            url = f'{HOST}{TOUR_PATH}'.format(group_id=group_id)
                            outgoing_funnel_response = requests.post(url, json.dumps(payload), params=params, headers=headers)

                            # If funnel returns an error
                            if outgoing_funnel_response.status_code < 200 or outgoing_funnel_response.status_code >= 300:
                                error_code, funnel_guestcard = self.save_guestcard_funnel(payload["client"], group_id, headers)
                                customer_id = funnel_guestcard['client']['id']
                                tour_error = json.loads(outgoing_funnel_response.text)["errors"]["appointment"]["start"][0]
                                available_time = self.get_available_times(group_id, appointment_date, headers)
                            # Success response of funnel
                            else:
                                 tour_schedule_id= json.loads(outgoing_funnel_response.text)["data"]["appointment"]["id"]
                            converted_date = datetime.strptime(tour_requested.replace("T", " ")[0:tour_requested.index("Z")].strip(), '%Y-%m-%d %H:%M:%S')
                            format_date = converted_date.strftime("%B %d, %Y")
                            hour = f'{converted_date.hour}:{converted_date.minute}'
                            payload["client"].update({"notes": comment + " --TOURS--Tour Scheduled for " + format_date + " at " + hour})
                            error_code, funnel_guestcard =  self.save_guestcard_funnel(payload["client"], group_id, headers)
                     
                            if error_code != 200:
                                return {
                                    'statusCode': error_code,
                                    'body': json.dumps({
                                        'data': [],
                                        'errors': [{"message": "Error saving guestcard in funnel"}]
                                    }),
                                    'headers': {
                                        'Content-Type': 'application/json',
                                        'Access-Control-Allow-Origin': '*',  
                                    },
                                    'isBase64Encoded': False  
                                } 

                            customer_id = funnel_guestcard['client']['id']
                            tour_information = {
                                    "availableTimes": available_time,
                                    "tourScheduledID": tour_schedule_id,
                                    "tourRequested": appointment_date,
                                    "tourSchedule": True if tour_schedule_id else False,
                                    "tourError": tour_error,
                                }
                        except Exception as e:
                             return {
                                    'statusCode': "500",
                                    'body': json.dumps({
                                        'data': [],
                                        'errors': [{"message": f"{e}"}]
                                    }),
                                    'headers': {
                                        'Content-Type': 'application/json',
                                        'Access-Control-Allow-Origin': '*',  
                                    },
                                    'isBase64Encoded': False  
                                } 
            error_code, funnel_guestcard = self.save_guestcard_funnel(payload["client"], group_id, headers)
            customer_id = funnel_guestcard['client']['id']
            if error_code == 200:
                serviceResponse = ServiceResponse(
                        guest_card_id= customer_id,
                        first_name=prospect["first_name"],
                        last_name=prospect["last_name"],
                        tour_information=tour_information,
                    ).format_response()
                

                return  {
                                'statusCode': "200",
                                'body': json.dumps({
                                    'data': serviceResponse,
                                    'errors': []
                                }),
                                'headers': {
                                    'Content-Type': 'application/json',
                                    'Access-Control-Allow-Origin': '*',  
                                },
                                'isBase64Encoded': False  
                            }
            
                    
        
          
    def get_available_times(self, group_id , date, headers):
            date = date.strip()[0:date.index('T')] 
        
            outgoing_funnel = f'{HOST}{AVAILABLE_TIMES_PATH}'.format(group_id=group_id, from_date=date, to_date=date)

            outgoing_funnel_response = requests.get(outgoing_funnel, headers=headers)
            response = json.loads(outgoing_funnel_response.text)
            formatted_datetime_strings = []

            # Iterate through the original datetime strings and remove the 'T'
            for datetime_str in response["available_times"]:
                formatted_datetime = datetime_str.replace('T', ' ')
                formatted_datetime_strings.append(formatted_datetime)
            return formatted_datetime_strings
                   
    
    def save_guestcard_funnel(self, body, group_id, headers):
          try:
            # Call outgoing to save the prospect into funnel
                body.update({"group" : group_id})
                outgoing = HOST+GUEST_CARD_PATH

                outgoing_response = requests.post(outgoing, json.dumps({"client" : body}), headers= headers)
                response =  json.loads(outgoing_response.text)
                # If errors
                if outgoing_response.status_code < 200 or outgoing_response.status_code >= 300:
                    return outgoing_response.status_code, response["message"]

                # Success case 
                return 200, response["data"]

          except Exception as e:
                logging.error(f"Error Funnel Guestcard: {e}")
                data = {
                    "data": {},
                    "error": [f"Error Funnel Guestcard: {e}"],
                }
                return 500, data
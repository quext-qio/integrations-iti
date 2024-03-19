import json, requests
from datetime import datetime
from configuration.realpage.realpage_config import ilm_config
from utils.mapper.bedroom_mapping import bedroom_mapping

class QuextTourService:

    # ----------------------------------------------------------------------------------------------
    # Saves Quext Tour
    @staticmethod
    def save_quext_tour(body: dict):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        source = body["source"].lower().replace("dh", "DIGITAL_HUMAN").replace("ws", "WEBSITES").replace("spa", "DIGITAL_HUMAN")
        preference = body['guestPreference']
        prospect = body['guest']

        bedroooms_data = []
        if "desiredBeds" in preference and isinstance(preference["desiredBeds"], list):
            bedroooms_data = [bedroom_mapping[preference] for preference in preference["desiredBeds"] if preference in bedroom_mapping]
        
        new_body  = {
            "customer_id": body["platformData"]["customerUUID"],
            "community_id": body["platformData"]["communityUUID"],
            "activity_source_name": source,
            "appointment_type_name": "IN_PERSON_TOUR",
            "desired_number_of_bedrooms": bedroooms_data,
            "max_budget": preference["desiredRent"] if "desiredRent" in preference else 0,
            "notes": body.get("guestComment", ""),
            "move_in_date": preference["moveInDate"].split("T")[0] if "moveInDate" in preference and preference["moveInDate"] else "",    
            "start_time": datetime.strptime(body["tourScheduleData"]["start"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S"),
            "guest": {
                "first_name": prospect["first_name"],
                "last_name": prospect["last_name"],
                "email": prospect["email"]
            },
        }

        if prospect.get("phone"):
            new_body["guest"]["phone_number"] = ''.join(filter(str.isdigit, prospect["phone"]))

        try:
            environment = ilm_config['environment']
            url = f"https://calendar.{environment}.quext.io/api/v1/appointments"
            quext_response = requests.post(url=url, data=json.dumps(new_body), headers=headers)
            response =  json.loads(quext_response.text)
            
            # If errors
            if quext_response.status_code < 200 or quext_response.status_code >= 300:
                data = {
                    "data": {},
                    "error": {
                        "message": response["message"]
                    },
                }
                return quext_response.status_code, data

            # Success case
            data = {
                "data": {
                    "id": response["appointment_id"]
                },
                "error": {},
            }
            return 200, data

        except Exception as e:
            print(f"Unhandled error trying to save tour into quext calendar: {e}")
            data = {
                "data": {},
                "error": {
                    "message": f"Unhandled error trying to save tour into quext calendar: {e}",
                },
            }
            return 500, data

    
    # ----------------------------------------------------------------------------------------------
    # Gets available times
    @staticmethod
    def get_available_times(ids: dict, date: str, partner: any, headers: dict):
        date = date.strip().split("T")[0]
        if partner == "Funnel":
            url = f"https://nestiolistings.com/api/v2/appointments/group/{partner['platformData']['communityID']}/available-times/?from_date={date}&to_date={date}"
            funnel_response = requests.get(url=url, data=json.dumps(body_request), headers=headers)
            response = json.loads(funnel_response.text)
            return response["available_times"]
        if partner == "Quext":
            body_request = {
                "timeData": {
                    "fromDate": date,
                    "toDate": date
                },
                "platformData": ids
            }
            environment = ilm_config['environment']
            url = f"https://calendar.{environment}.quext.io/api/v1/time-slots/public"
            quext_response = requests.post(url=url, data=json.dumps(body_request), headers=headers)
            return json.loads(quext_response.text)["available_times"]
    
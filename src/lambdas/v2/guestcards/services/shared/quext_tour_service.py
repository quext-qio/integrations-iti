import json, requests
from configuration.realpage.realpage_config import ilm_config

class QuextTourService:

    # ----------------------------------------------------------------------------------------------
    # Saves Quext Tour
    @staticmethod
    def save_quext_tour(body: dict):
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        }
        source = body["source"].lower().replace("dh", "digital human").replace("ws", "websites").replace("spa", "digital human")
        preference = body['guestPreference']
        prospect = body['guest']
        
        new_body  = {
                "appointmentData": {
                    "firstName": prospect["first_name"],
                    "lastName": prospect["last_name"],
                    "email": prospect["email"],
                    "phone": "" if not "phone" in prospect else prospect["phone"],
                    "layout": preference["desiredBeds"],
                    "priceCeiling": preference["desiredRent"] if "desiredRent" in preference else 0,
                    "moveInDate": preference["moveInDate"].split("T")[0] if "moveInDate" in preference and preference["moveInDate"] else "",
                    "notes": body["guestComment"],
                    "start": body["tourScheduleData"]["start"],
                    "source": source
                },
                "platformData": body["platformData"],
            }
        try:
            environment = ilm_config['environment']
            url = f"https://calendar.{environment}.quext.io/api/v1/appointments/public"
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
    
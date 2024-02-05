import requests, os, json, uuid, logging
from datetime import datetime, timedelta
from Utils.Convert import Convert
from Utils.Config.Config import config
from Utils.Constants.TourIntegrationConstants import Tour_Integration_Constants
from Utils.Constants.EntrataConstants import EntrataConstants

class DataEntrata:

    def get_tour_availability(self, ips, data):
      
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {config['entrata_api_key']}" 
            }
        _headers = headers

        # Getting parameter from payload
        toDate_original = data["timeData"]["toDate"]

        toDate_datetime = datetime.strptime(toDate_original, "%Y-%m-%d")

        toDate = toDate_datetime - timedelta(days=1)

        data["timeData"]["toDate"]  = toDate.strftime("%Y-%m-%d")

        _body = {
            EntrataConstants.PROPERTYID: ips["foreign_community_id"],
            EntrataConstants.FROM_DATE: Convert.format_date(data["timeData"]["fromDate"],
                                                            EntrataConstants.QUEXT_DATE_FORMAT,
                                                            EntrataConstants.ENTRATA_DATE_FORMAT),
            EntrataConstants.TO_DATE: Convert.format_date(data["timeData"]["toDate"],
                                                        EntrataConstants.QUEXT_DATE_FORMAT,
                                                        EntrataConstants.ENTRATA_DATE_FORMAT)}
        request_body = {
                "auth": {
                    "type": "basic"
                },
                "requestId": str(uuid.uuid1()),
                "method": {
                    "name": str(EntrataConstants.GET_CALENDAR_AVAILABILITY),
                    "version": "r1",
                    "params": _body
            }
        }

        _params = {
            "method": str(EntrataConstants.GET_CALENDAR_AVAILABILITY)
        }

        outgoing_entrata = f'{config["entrata_host"]}/api/properties'
        response = requests.post(outgoing_entrata, data=json.dumps(request_body), params=_params, headers=_headers)
        # Checking for Empty list
        response = json.loads(response.text)
        if "error" in response[EntrataConstants.RESPONSE]:
            logging.info("Got no records for Tour Availability from Entrata")
            return [], {"message": response[EntrataConstants.RESPONSE]["error"]["message"] }
        res = (response[EntrataConstants.RESPONSE][EntrataConstants.RESULT][
                EntrataConstants.PROPERTY_CALENDAR_AVAILABILITY])
        for value in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            start_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.START_TIME]
            end_time = value[EntrataConstants.DATE]+' '+value[EntrataConstants.END_TIME]
            
            start_time = Convert.convert_datetime_timezone(start_time, EntrataConstants.ENTRATA_TIMEZONE,
                                                            EntrataConstants.QUEXT_TIMEZONE,  
                                                            EntrataConstants.DATETIME_FORMAT, 
                                                            Tour_Integration_Constants.DATETIME)
            end_time = Convert.convert_datetime_timezone(end_time, EntrataConstants.ENTRATA_TIMEZONE, 
                                                            EntrataConstants.QUEXT_TIMEZONE, 
                                                            EntrataConstants.DATETIME_FORMAT, 
                                                            Tour_Integration_Constants.DATETIME)
            start_time = start_time.split(' ')
            end_time = end_time.split(' ')
            if start_time[0] and end_time[0]:
                value[EntrataConstants.DATE] = start_time[0]
                value[EntrataConstants.START_TIME] = start_time[1]
                value[EntrataConstants.END_TIME] = end_time[1]
        time_slot = []
        for items in res[EntrataConstants.AVAILABLE_HOURS][EntrataConstants.AVAILABLE_HOUR]:
            starttime = items[EntrataConstants.DATE] + 'T'+ items[EntrataConstants.START_TIME]
            endtime = items[EntrataConstants.DATE] + 'T' + items[EntrataConstants.END_TIME]
            time_slot.append({EntrataConstants.START_TIME: starttime, EntrataConstants.END_TIME: endtime })
            availableTimes = Convert.generate_time_slots(time_slot)
        
        # Convert all dates to military time format
        military_time_dates = [convert_to_military_time(date) for date in availableTimes if 8 <= int(date.split()[1].split(":")[0]) < 17]

        return military_time_dates, {}
    
    # Function to convert to military time format
def convert_to_military_time(date_str):
    # Convert the date string to a datetime object
    date_datetime =  datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    # Format the date in military time format
    military_time_date = date_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return military_time_date





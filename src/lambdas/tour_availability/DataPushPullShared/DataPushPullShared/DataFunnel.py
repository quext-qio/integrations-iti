import logging, json, os, requests
from Utils.Config.Config import config
from Utils.Constants.Constants import Constants

class DataFunnel:


    def get_tour_availability(self, ips, event):
        """
        Get Tour availability information
        """
        _params = {
            "group_id": ips["platformData"]["communityID"],
            "from_date": event["timeData"].get("fromDate", ""),
            "to_date": event["timeData"].get("toDate", ""),
        }
        url = f"{Constants.FUNNEL_HOST}/api/v2/appointments/group/{_params['group_id']}/available-times/"

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=_params)

        response = response.text

        #If exist an error from funnel
        if not "available_times" in response:
            error = response['errors'] if "errors" in response else response

            return [], error

        # If empty response, return an error
        data = response["available_times"]
        if len(data) == 0:
            logging.warn("Funnel services is not responding or has provided an empty payload.")
            return [], {"message": "Please contact the leasing office by phone to schedule a tour."}

        # Remove T of datetime
        new_data = []
        for date in data:
            list_date = date.split("T")
            new_date = f"{list_date[0]} {list_date[1]}"
            new_data.append(new_date)
        return new_data, []
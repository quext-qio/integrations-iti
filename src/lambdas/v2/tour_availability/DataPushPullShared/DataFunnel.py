import logging, json, os, requests
from Utils.Config.Config import config
from Utils.Constants.FunnelConstants import FunnelConstants

class DataFunnel:


    def get_tour_availability(self, ips, event):
        """
        Get Tour availability information
        """
        _params = {
            "group_id": ips[FunnelConstants.PLATFORM_DATA][FunnelConstants.FOREIGN_COMMUNITY_ID],
            "from_date": event[FunnelConstants.TIME_DATA].get(FunnelConstants.FROM_DATE, ""),
            "to_date": event[FunnelConstants.TIME_DATA].get(FunnelConstants.TO_DATE, ""),
        }
        url = f"{FunnelConstants.FUNNEL_HOST}{FunnelConstants.FUNNEL_PATH}{_params[FunnelConstants.GROUP_ID]}/available-times/"

        headers = {
            'Content-Type': FunnelConstants.CONTENT_TYPE,
            'Authorization': f'Basic {config[FunnelConstants.FUNNEL_API_KEY]}',
        }

        response = requests.get(url, headers=headers, params=_params)

        response = json.loads(response.text)

        #If exist an error from funnel
        if not FunnelConstants.AVAILABLE_TIMES in response:
            error = response[FunnelConstants.ERRORS] if "errors" in response else response

            return [], error

        # If empty response, return an error
        data = response[FunnelConstants.AVAILABLE_TIMES]
        # Remove T of datetime
        new_data = []
        for date in data:
            list_date = date.split("T")
            new_date = f"{list_date[0]} {list_date[1]}"
            new_data.append(new_date)
    
        return new_data, {}
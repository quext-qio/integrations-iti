import requests, json
from utils.shared.constants.guestcard_constants import GuestcardsConstants
from utils.mapper.bedroom_mapping import bedroom_mapping
from utils.shared.config import config
from urllib.parse import urlencode

class PayladHandler:

    def builder_payload(self, payload, events):
        guest = payload[GuestcardsConstants.GUEST]
        guest_preference = payload[GuestcardsConstants.GUEST_PREFERENCE]
        # Get values of bedroooms
        bedroooms_data = []
        if "desiredBeds" in guest_preference:
            # Map string to int using [bedroom_mapping]
            for i in range(len(guest_preference["desiredBeds"])):
                string_beds = guest_preference["desiredBeds"][i]
                bedroooms_data.append(bedroom_mapping.get(string_beds, 0))

        builder_payload = {
                "LeadManagement": {
                    "Prospects": {
                        "Prospect": {
                            "Customers": {
                                "Customer": {
                                    "@Type": "prospect",
                                    "Name": {
                                        "FirstName": guest[GuestcardsConstants.FIRST_NAME],
                                        "LastName": guest[GuestcardsConstants.LAST_NAME]
                                    },
                                    "Phone": {
                                        "@Type": "cell",
                                        "PhoneNumber": guest.get(GuestcardsConstants.PHONE, "")
                                    },
                                    "Email": guest[GuestcardsConstants.EMAIL],
                                }
                            },
                            "CustomerPreferences": {
                                "TargetMoveInDate": guest_preference.get(GuestcardsConstants.MOVE_IN_DATE, ""),
                                "DesiredRent": {
                                    "@Exact": str(guest_preference.get(GuestcardsConstants.DESIRED_RENT, ""))
                                },
                                "DesiredNumBedrooms": {
                                        "@Min": min(bedroooms_data) if len(bedroooms_data) > 0 else 0,
                                        "@Max": max(bedroooms_data) if len(bedroooms_data) > 0 else 0
                                },
                                "DesiredLeaseTerm": guest_preference.get(GuestcardsConstants.LEASE_TERM, 0),
                                "NumberOfOccupants": guest_preference.get(GuestcardsConstants.OCCUPANTS, 0),

                                "Comment": guest_preference.get(GuestcardsConstants.MOVE_IN_REASON, ""),

                            },
                            "Events": events
                        }

                    }
                }
            }
        return builder_payload


    def create_events(self, data, ips):
            agent_id, first_name, last_name = self.get_agent_info(data["Source"], ips)
            events = {
                            "Event": {
                                "@EventType": data[GuestcardsConstants.EVENT_TYPE],
                                "@EventDate": data[GuestcardsConstants.EVENT_DATE],
                                "EventID": {
                                    "@IDValue": "",
                                    "@IDType":  data.get("unitID", "")
                                },
                                "Agent": {
                                    "AgentID": {
                                        "@IDValue": agent_id
                                    },
                                    "AgentName": {
                                        "FirstName": first_name,
                                        "LastName": last_name
                                    }
                                },
                                "FirstContact": "true",
                                "Comments": data.get("Comments", ""),
                                "TransactionSource": data.get("TransactionSourceid")
                            }
                    } 
            
            return events
 
    def get_agent_info(self, source, ips):
        if ips["purpose"]["guestCards"]["partner_name"] == "Spherexx":
            agent_id, first_name, last_name = "", "",""
        agent_id, last_name = "", ""
        if source == "ws":
            last_name = GuestcardsConstants.WEBSITES
        elif source == "dh":
            last_name = GuestcardsConstants.DIGITAL_HUMAN
        body = { 
            "PropertyID": config["resman_property_id"],
            "AccountID": config["resman_account_id"],
            "IntegrationPartnerID": config['Integration_partner_id'],
            "ApiKey": config['ApiKey']
            }
        first_name = GuestcardsConstants.SOURCE
        url = f'https://api.myresman.com/Leasing/GetEmployees'
        _body = urlencode(body, {"Content-type": "application/x-www-form-urlencoded"})
    
        # Prepare the headers
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Content-Length': str(len(_body))
        }
        
    
        # Send the HTTP POST request
        resmanChannelResponse = requests.post(url, data=_body, headers=headers)
        employees = json.loads(resmanChannelResponse.text)
        for agent in employees["Employees"]:
            if last_name in agent["Name"]:
                agent_id = agent["ID"] 
        return agent_id, first_name, last_name
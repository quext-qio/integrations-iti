import json
from abstract.service_interface import ServiceInterface
from utils.mapper.bedroom_mapping import bedroom_mapping
class RealPageILMService(ServiceInterface):
    def get_data(self, body: dict):
        # Create body for RealPage ILM

        # TODO: Get values of [realpage_property, realpage_id] depend of RealPage Type
        realpage_property = "ILM Property Id"
        realpage_id = "UAT80P11"
        body_realpage_ilm = self.create_body_realpage_ilm(body, realpage_property, realpage_id)







        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': body_realpage_ilm,
                'errors': []
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
    
    # Creates a body of RealPage ILM endpoint
    def create_body_realpage_ilm(self, body: dict, realpage_property: str, realpage_id: str) -> dict:
        guest = body["guest"]
        guestPreference = body["guestPreference"]

        # Get values of bedroooms
        bedroooms_data = []
        if "desiredBeds" in guestPreference:
            # Map string to int using [bedroom_mapping]
            for i in range(len(guestPreference["desiredBeds"])):
                string_beds = guestPreference["desiredBeds"][i]
                bedroooms_data.append(bedroom_mapping.get(string_beds, 0))

        # Create new body
        new_body = {
            "Prospects": [
                {
                    "TransactionData": {
                        "Identification": [
                            {
                                "IDType": realpage_property,
                                "IDValue": realpage_id
                            },
                            {
                                "IDType":"GoogleID", 
                                "IDValue":"Quext" 
                            }    
                        ]
                    },
                    "Customers": [
                        {
                            "Name": {
                                "FirstName": guest["first_name"],
                                "LastName": guest["last_name"]
                            },
                            "Phone": [
                                {
                                    "PhoneType": "cell",
                                    "PhoneNumber": guest["phone"] if "phone" in guest else ""
                                }
                            ],
                            "Email": guest["email"] if "email" in guest else "",
                        }
                    ],
                    "CustomerPreferences": {
                        "TargetMoveInDate": guestPreference["moveInDate"],
                        "DesiredRent": {
                            "Max": guestPreference["desiredRent"] if "desiredRent" in guestPreference else 0
                        },
                        "DesiredNumBedrooms": {
                            "Min": min(bedroooms_data) if len(bedroooms_data) > 0 else 0,
                            "Max": max(bedroooms_data) if len(bedroooms_data) > 0 else 0
                        },
                        "Comment": body["guestComment"] if "guestComment" in body else ""
                    },
                    
                }
            ]
        }
        #  TODO: Validate if [Date] in body

        return new_body
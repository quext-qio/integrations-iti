import json
import requests
import os
from AccessControl import AccessUtils as AccessControl

class DataController:
    def __init__(self, logger):
        self.logger = logger

    def get_customers(self, customer_uuid, wsgi_input):
        errors = []
        auth_host = os.environ['AUTH_HOST']
        url = f'{auth_host}/service/api/v1/customers/{customer_uuid}'  
        payload = {}
        headers = {
        'accept': 'application/json'
        }

        authChannelResponse = requests.request("GET", url, headers=headers, data=payload)
        #Get credentials
        res, res_code= AccessControl.check_access_control(wsgi_input)
        if res_code != 200:
            return res_code, res
    
        # Expect only 200 status codes here, let's do some error handling.
        if authChannelResponse.status_code != 200:
            errors.append({ "status_code": authChannelResponse.status_code,
                            "status": "error",
                            "debug": authChannelResponse.url,
                            "message": authChannelResponse.text })
            response = { "data": { "provenance": [ "authapi" ], }, "errors": errors }
        else:
            customers = []
            if customer_uuid != "":
                customers.append(json.loads(authChannelResponse.text))
            else:
                customerJSON = json.loads(authChannelResponse.text)["content"]
                for c in customerJSON:
                    if c["deletedAt"] == None:
                        customers.append({
                                "customerUUID": c["id"],
                                "name": c["name"],
                                "propertiesCount": len(c["communities"]),
                                "created": c["createdAt"], 
                            })
            response = { "data": { "provenance": [ "auth-service" ], "customers": customers }, "errors": [] }

        return authChannelResponse.status_code, response

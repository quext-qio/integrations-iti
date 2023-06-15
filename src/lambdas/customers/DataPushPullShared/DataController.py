import json
import requests
import os

class DataController:
    def __init__(self, logger):
        self.logger = logger

    def get_customers(self, customer_uuid):
        errors = []
        auth_host = os.environ.get('AUTH_HOST')
        url = f'{auth_host}/service/api/v1/customers/{customer_uuid}'  
        payload = {}
        headers = {
        'accept': 'application/json'
        }

        authChannelResponse = requests.request("GET", url, headers=headers, data=payload)

        # if res:
        #     return
        
        # with authapi will no longer be needed. Will keep this in, commented out, for development purposes.
        # jwt = "Bearer eyJraWQiOiJxNFczSlRCdjFhaVdXUFVxNXA4TVwvUjE5Yk5qdlNNeUdUSk5WZFZIc3c2cz0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhYzgzNDJiNS03YmE3LTQyZjEtYjJiYS1mMzA4NjFiYjIxMGEiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfcUxpeVRmVlZHIiwiY29nbml0bzp1c2VybmFtZSI6Ijg2NDliOGRkLTYxNDctNDk4OS1hMTI4LWY2YTE2MjI1OWVkZCIsIm9yaWdpbl9qdGkiOiJmYWRlZjQzNC01NWEzLTQ5YmEtOGM0Yy03YjdlZTBhYjFlMWUiLCJhdWQiOiIxOGNudDRwcG5lN2NsaXI3YzhpMjR0cmhmMiIsImV2ZW50X2lkIjoiNDkzNGY3YjAtYzUwZi00YTIzLTlkZWEtOGQyMmFhN2RkNDU2IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE2NDk5NTU4MDksImV4cCI6MTY0OTk1OTQwOSwiaWF0IjoxNjQ5OTU1ODA5LCJqdGkiOiJmZjRkZDMzMS01NWU4LTQxZWItODg1My0wMGM0MjVkNWVmNWEiLCJlbWFpbCI6ImpvaG4ub3lsZXJAb25lcXVleHQuY29tIn0.mN8WNp1nWI6clnjI203_htuk4s44Swr8rdPG1SjCdiKYD4s0d1_rRcV4abubYCDjArnviE1k808Gv04UEdkT6T2ngNWxkLHx4pf2-OrlZBOz-VqXg9rIQv8ycYPr2Ex13drta6PPAqdfQuKnpGi6XNOq1gP7PVM9T_r7kTfl7Ci6Ko0Eh4HkYhzI-oU4V-tKv6MgQLOPVrg_1NNFmYm9j_fazKfDXL8rSewCxpqaBu_LDyfvICI9TYAmNSc9EgmQTyQOFbHQRMcgVRe5FIEPrROiBUMXdjgxnLufyPKqMEQYqz7CXh5ZjsVj2lKvun2Dl8SuKGatOlabUiVPnCJSNQ"
        # headers = {'Authorization': jwt, 'X-Customer-User-Id': "68cdf716-ba9b-4955-b490-b636cde0991f" }
        
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

        return response

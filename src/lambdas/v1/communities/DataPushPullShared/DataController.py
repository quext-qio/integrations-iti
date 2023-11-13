import json
import requests
import os
from AccessControl import AccessUtils as AccessControl
class DataController:
    def __init__(self, logger):
        self.logger = logger

    def get_communities(self, customer_uuid, wsgi_input):
        errors = []
        #auth_host = os.environ['AUTH_HOST']
        auth_host = "https://api.internal.dev.quext.io"
        url = f'{auth_host}/service/api/v1/customers/{customer_uuid}/communities'
                
        payload = {}
        headers = {
        'accept': 'application/json'
        }
        # Lógica para obtener los datos de las comunidades utilizando self.outgoing_channel y customer_uuid
        authChannelResponse = requests.request("GET", url, headers=headers, data=payload)

         # Get credentials
        res, res_code= AccessControl.check_access_control(wsgi_input)
        if res_code != 200:
            return res_code, res

        # Expect only 200 status codes here, let's do some error handling
        communities = []
        if authChannelResponse.status_code != 200:
            errors.append({ "status_code": authChannelResponse.status_code, 
                            "status": "error", 
                            "message": authChannelResponse.text })
            response = { "data": { "provenance": [ "auth-service" ], }, "errors": errors }
        else:
            communityJSON = json.loads(authChannelResponse.text)["content"]

            for c in communityJSON:
                if c["deletedAt"] == None:
                    communities.append({ "customerUUID": customer_uuid,
                                        "communityUUID": c["id"], 
                                        "name": c["name"], 
                                        "customer": c["ownerName"],
                                        "contactInformation": {
                                            "timezone": c["timezoneId"],
                                            "phoneVoice": c["phone"],
                                            "phoneSms": c["smsPhone"],
                                            "email": c["email"],
                                            "emailLeasing": c["leasingEmail"],
                                            "emailPayment": c["onlinePaymentEmail"],
                                            "web": c["websiteUrl"],
                                            "address": {
                                                "street": c["address"]["addressLine1"],
                                                "street2": c["address"]["addressLine2"],
                                                "city": c["address"]["city"],
                                                "state": c["address"]["state"],
                                                "zip": c["address"]["zip"],
                                            },
                                            "mail": {
                                                "street": c["mailingAddress"]["addressLine1"],
                                                "street2": c["mailingAddress"]["addressLine2"],
                                                "city": c["mailingAddress"]["city"],
                                                "state": c["mailingAddress"]["state"],
                                                "zip": c["mailingAddress"]["zip"],
                                            }
                                        },
                                        "socialMedia": {
                                            "homepage": c["corporateUrl"],
                                            "facebook": c["facebookUrl"],
                                            "twitter": c["twitterUrl"],
                                            "instagram": c["instagramUrl"],
                                            "pinterest": c["pinterestUrl"],
                                        },
                                        "branding": {
                                            "logoId": c["communityLogoId"],
                                            "logo": c["communityLogoUrl"],
                                            "imageId": c["communityImageId"],
                                            "image": c["communityImageUrl"],
                                        }
                                    }
                )

            response = { "data": { "provenance": [ "auth-service" ], "communities": communities }, "errors": [] }


        response = {
            "data": {
                "provenance": ["auth-service"],
                "communities": communities
            },
            "errors": errors
        }

        return authChannelResponse.status_code, response

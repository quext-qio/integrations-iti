import requests, json, os

class IPSController:

    def get_platform_data(self, community_id:str, customer_id:str, purpose:str):
        try:
            ips_host = os.environ['IPS_HOST']
            url = f'{ips_host}/api/read-configuration/{customer_id}/{community_id}/{purpose}'
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url, headers=headers)
            return 200, response
        except Exception as e:
            print(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"
    
    def get_list_partners(self, community_id):
        try:
            ips_host = os.environ['IPS_HOST']
            url = f'{ips_host}/api/community/{community_id}/partners'
            payload = {}
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("GET", url, headers=headers, data=payload)

            return 200, response
        except Exception as e:
            print(f"Error IPS endpoint: {e}")
            return 500, f"Error from IPS: {e}"



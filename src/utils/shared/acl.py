import json, os, requests

class ACL:
    @staticmethod
    def _loadSecurity() -> tuple:
        parameter_store = json.loads(os.environ.get("parameter_store"))
        host = parameter_store['ACL_HOST']
        url = f'{host}/api/partners/security?redacted=off'
        response = requests.get(url)
        if response.status_code == 200:
            return True, response
        else:
            return False, response

    @staticmethod
    def check_permitions(endpoint, method, api_key):
        # Load security from ACL
        is_ok, response = ACL._loadSecurity()
        if not is_ok:
            return False, response
        
        # Success response from ACL endpoint
        for i in json.loads(response.text)["content"]:
            security_item = i["security"]
            print(f"security_item: {security_item}")
            if "apiKey" in security_item:
                if security_item["apiKey"] == api_key:
                    print(f"apiKey found: {security_item['apiKey']}")
                    for e in security_item["endpoints"]:
                        if e["uri"] == endpoint and method in e["verbs"]:
                            # Success case
                            return True, response
        
        return False, response
        
        

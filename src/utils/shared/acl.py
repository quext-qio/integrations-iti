import json, os, requests

class ACL:
    def _loadSecurity(self, partner) -> tuple:
        parameter_store = json.loads(os.environ.get("parameter_store"))
        host = parameter_store['ACL_HOST']
        url = f'{host}/api/partners/security/{partner}?redacted=off'
        response = requests.get(url)
        if response.status_code == 200:
            return True, response
        else:
            return False, response

    @staticmethod
    def check_permitions(self, endpoint, method, api_key):
        # Load security from ACL
        is_ok, response = self._loadSecurity()
        if not is_ok:
            return False, response
        
        # Success case
        for i in json.loads(response.text)["content"]:
            security_item = i["security"]
            if security_item["apiKey"] == api_key:
                for e in security_item["endpoints"]:
                    if e["uri"] == endpoint and method in e["verbs"]:
                        return True, response
                return False, response
        
        

import json
import logging
import os
import requests

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class AccessControl():
    def __init__(self):
        self.ACLs = []

    def load_acls(self, partner=""):
        
        parameter_store = json.loads(os.environ.get("parameter_store"))
        host = parameter_store['ACL_HOST']
        url = f'{host}/api/partners/security/{partner}?redacted=off'
        response = requests.get(url)
        # If outgoing return an error
        if response.status_code != 200:
            logging.info(response.text)
            return False, response, self.ACLs
        # Success case
        loop_ACLs = []
        for i in json.loads(response.text)["content"]:
            loop_ACLs.append(i["security"])
        self.ACLs = loop_ACLs.copy()
        return True, response, self.ACLs

    def get_acls(self):
        return self.ACLs


class AccessUtils:


    @staticmethod
    def accessControl(wsgi_environ, ACLs):
        wsgi = wsgi_environ
        endpoint = wsgi['PATH_INFO']
        verb = wsgi['REQUEST_METHOD']
        try:
            api_key = wsgi['HTTP_X_API_KEY']
        except KeyError:
            return None, "No API key header."
        if api_key is None:
            return None, "No API key value."
        try:
            for d in ACLs:
                if "apiKey" in d and d["apiKey"] == api_key:
                    if "endpoints" not in d:
                        return None, "No permission for any endpoint is defined."
                    for e in d["endpoints"]:
                        if "uri" in e and "verbs" in e and e["uri"] == endpoint and verb in e["verbs"]:
                            return e["acl"], "good"
                        elif "uri" in e and e["uri"] == endpoint:
                            return None, "No permission for this HTTP method."
                    return None, "No permission for this endpoint."
            return None, "Unknown API key."
        except Exception as e:
            logging.warning(f"Error Get ACLs: {e}")

    @staticmethod
    def accessControl_v2(wsgi_environ, ACLs):
        wsgi = wsgi_environ
        endpoint = wsgi['PATH_INFO']
        verb = wsgi['REQUEST_METHOD']
        try:
            api_key = wsgi['HTTP_AUTHORIZATION']
        except KeyError:
            return None, "No API key header."
        if api_key is None:
            return None, "No API key value."
        
        # Stripping Bearer prefix to validate apikey
        api_key = api_key.strip("Bearer ")
        try:
            for d in ACLs:
                if "apiKey" in d and d["apiKey"] == api_key:
                        if "endpoints" not in d:
                            return None, "No permission for any endpoint is defined."
                        for e in d["endpoints"]:
                            if "uri" in e and "verbs" in e and e["uri"] == endpoint and verb in e["verbs"]:
                                return e["acl"], "good"
                            elif "uri" in e and e["uri"] == endpoint:
                                return None, "No permission for this HTTP method."
                        return None, "No permission for this endpoint."
            return None, "Unknown API key."
        except Exception as e:
            logging.warning(f"Error Get ACLs: {e}")

    @staticmethod
    def externalCredentials(wsgi_environ, partner):
        access_control = AccessControl()
        ACLs = access_control.get_acls()
        wsgi = wsgi_environ
        api_key = wsgi['HTTP_X_API_KEY']
        if api_key is None:
            return None, "No API key value."
        try:
            for d in ACLs:
                if "apiKey" in d and d["apiKey"] == api_key:
                    if "credentials" not in d:
                        return None, "No credentials defined for any partner."
                    for e in d["credentials"]:
                        if "partner" in e and e["partner"] == partner:
                            headers = {}; body = {}
                            if "headers" in e:
                                headers = e["headers"]
                            if "body" in e:
                                body = e["body"]
                            return { "headers": headers, "body": body }, "good"
                    return None, "No credentials defined for specified partner."
            return None, "Unknown API key."
        except Exception as e:
            logging.warning(f"Error Get Credentials: {e}")

    @staticmethod
    def return_response(acl, status):

        if acl is None:
            if status == "No API key header.":
                return { "errors": [ { "message": status } ] } , 401
            else:
                return { "errors": [ { "message": status } ] } , 403
        return {}, 200

    @staticmethod
    def check_access_control(wsgi_environ):
        """
            args:
                wsgi_environ = self.wsgi_environ
        """
        access_control = AccessControl()
        access_util_obj = AccessUtils()
        ACLs = access_control.get_acls()
        is_ok = False
        acl_response = {
            "data": None
        }

        is_ok, acl_response, ACLs =  access_control.load_acls()
        # if len(ACLs) == 0:
        #     is_ok, acl_response, ACLs =  access_control.load_acls()
        if not is_ok:
            logging.warning(f"Error to load acls: {acl_response}")
            return {"error": f"Error to load acls {acl_response}"}, acl_response.status_code
        
        acl, status = access_util_obj.accessControl(wsgi_environ, ACLs)
        logging.info(status)
        response, status = access_util_obj.return_response(acl, status)
        return response, status

    @staticmethod
    def check_access_control_v2(wsgi_environ):
        """
            args:
                wsgi_environ = self.wsgi_environ
        """
        access_control = AccessControl()
        access_util_obj = AccessUtils()
        ACLs = access_control.get_acls()
        is_ok = False
        acl_response = {
            "data": None
        }
        if len(ACLs) == 0:
            is_ok, acl_response, ACLs = access_control.load_acls()
        if not is_ok:
            logging.warning(f"Error to load acls: {acl_response}")
        acl, status = access_util_obj.accessControl_v2(wsgi_environ, ACLs)
        logging.info(status)
        response, status_code = access_util_obj.return_response(acl, status)
        return response, status_code

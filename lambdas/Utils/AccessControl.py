import json
import logging
import os
import requests
from dotenv import load_dotenv
load_dotenv('docker/local.env')


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
        host = os.getenv('ACL_HOST')
        response = requests.get(f'{host}/api/partners/security/{partner}?redacted=off')
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
    def accessControl(wsgi_environ, logger, ACLs):
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
            logger.error(f"Error Get ACLs: {e}")

    @staticmethod
    def accessControl_v2(wsgi_environ, logger, ACLs):
        wsgi = wsgi_environ
        endpoint = wsgi['PATH_INFO']
        verb = wsgi['REQUEST_METHOD']
        try:
            api_key = wsgi['HTTP_AUTHORIZATION']
        except KeyError:
            return None, "No API key header."
        if api_key is None:
            return None, "No API key value."

        api_key = api_key.strip("Bearer ") # Stripping Bearer prefix to validate apikey
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
            logger.error(f"Error Get ACLs: {e}")

    @staticmethod
    def externalCredentials(wsgi_environ, logger, partner):
        access_control = AccessControl()
        ACLs = access_control.load_acls()[2]
        wsgi = wsgi_environ
        api_key = wsgi['HTTP_X_API_KEY']
        print(api_key, ": API_KEY")
        print(ACLs, ": ACLs")
        if api_key is None:
            return None, "No API key value."
        try:
            for d in ACLs:
                print("ACLs: ", d)
                if "apiKey" in d and d["apiKey"] == api_key:
                    if "credentials" not in d:
                        return None, "No credentials defined for any partner."
                    for e in d["credentials"]:
                        print("d['credentials']: ", e)
                        if "partner" in e and e["partner"] == partner:
                            headers = {}; body = {}
                            if "headers" in e:
                                headers = e["headers"]
                            if "body" in e:
                                body = e["body"]
                            print(headers, body)
                            return { "headers": headers, "body": body }, "good"
                    return None, "No credentials defined for specified partner."
            return None, "Unknown API key."
        except Exception as e:
            logger.error(f"Error Get Credentials: {e}")

    @staticmethod
    def return_response(response, acl, status):
        if acl is None:
            if status == "No API key header.":
                response.status_code = 401
                response.payload = json.dumps( { "errors": [ { "message": status } ] } )
            else:
                response.status_code = 403
                response.payload = json.dumps( { "errors": [ { "message": status } ] } )
            return True

    @staticmethod
    def check_access_control(wsgi_environ, logger, response):
        """
            args:
                wsgi_environ = self.wsgi_environ
                logger = self.logger
                response = self.response
        """
        access_control = AccessControl()
        access_util_obj = AccessUtils()
        ACLs = access_control.get_acls()
        is_ok = False
        acl_response = {
            "data": None
        }
        if len(ACLs) == 0:
            is_ok, acl_response, ACLs =  access_control.load_acls()
        if not is_ok:
            logger.error(f"Error to load acls: {acl_response}")
        acl, status = access_util_obj.accessControl(wsgi_environ, logger, ACLs)
        logger.info(status)
        response_code = access_util_obj.return_response(response, acl, status)
        return response_code

    @staticmethod
    def check_access_control_v2(wsgi_environ, logger, response):
        """
            args:
                wsgi_environ = self.wsgi_environ
                logger = self.logger
                response = self.response
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
            logger.error(f"Error to load acls: {acl_response}")
        acl, status = access_util_obj.accessControl_v2(wsgi_environ, logger, ACLs)
        logger.info(status)
        response_code = access_util_obj.return_response(response, acl, status)
        return response_code

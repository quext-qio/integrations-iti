import json, os, requests
from host.url_handler import UrlHandler

# It handles the host depend of stage
UrlHandler = UrlHandler(os.environ['CURRENT_ENV'])
API_KEY = os.environ['API_KEY']
CONSUMER_ID = os.environ['CONSUMER_ID']


class ACL:
    @staticmethod
    def _loadSecurity() -> tuple:
        url = f'{UrlHandler.get_ips_v2_host()}/api/v2/partner/partner-security/security-v1'
        print(f"ACL URL: {url}")
        headers = {
            'Content-Type': 'application/json',
            'apikey': API_KEY,
            'x-ips-consumer-id': CONSUMER_ID
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, response
        else:
            return False, response

    @staticmethod
    def check_permitions(event, check_endpoints=True):
        
        # Case: No API key in header or empty
        if 'x-api-key' not in event['headers'] or event['headers']['x-api-key'] == "":
            print("Unauthorized: No API key found")
            return False, {
                'statusCode': "401",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": "API key is required"}],
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False
            }

        # Create values required for [ACL.check_permitions]
        endpoint = event['resource']
        method = event["httpMethod"]
        api_key = event['headers']['x-api-key']

        # Load security from ACL
        is_ok, response = ACL._loadSecurity()
        if not is_ok:
            print(f"Bad Gateway from ACL endpoint: {response}")
            # Case: ACL endpoint not available or has error
            return False, {
                'statusCode': "502",
                'body': json.dumps({
                    'data': {},
                    'errors': [{"message": "We're sorry, but we couldn't retrieve the list of access control lists at the moment. IPS service that handles this request is experiencing technical difficulties. Please try again later."}],
                }),
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',  
                },
                'isBase64Encoded': False
            }
        
        # Case: Success response from ACL endpoint
        for i in response.json():
            security_item = i["security"]
            if "apiKey" in security_item:
                if security_item["apiKey"] == api_key:
                    print(f"apiKey found: {security_item['apiKey']}")
                    if not check_endpoints:
                        # Case: Just check if API key exists
                        return True, []
                    if "endpoints" not in security_item:
                        return False, {
                            'statusCode': "401",
                            'body': json.dumps({
                                'data': {},
                                'errors': [{"message": "No permission for any endpoint is defined"}],
                            }),
                            'headers': {
                                'Content-Type': 'application/json',
                                'Access-Control-Allow-Origin': '*',  
                            },
                            'isBase64Encoded': False
                        }
                    # Loop endpoints
                    for e in security_item["endpoints"]:
                        if e["uri"] == endpoint and method in e["verbs"]:
                            # Case: success, will return true and ACL list
                            return True, e["acl"]
        
        # Case: API key not found
        return False, {
            'statusCode': "401",
            'body': json.dumps({
                'data': {},
                'errors': [{"message": "Unknown API key"}],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False
        }
        
        

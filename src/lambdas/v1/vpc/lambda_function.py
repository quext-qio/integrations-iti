import json, requests

def lambda_handler(event, context):
    print(f"VPC handler: {event}")
    try:
        # Success case
        url = "https://partner-api.internal.dev.quext.io/api/partners/security/?redacted=off"
        response = requests.get(url=url)

        if response.status_code == 200:
            print(f"Success: {response.text}")
        else:
            print(response)
        return {
            'headers': {
                'Content-Type': 'application/json'
            },
            'statusCode': 200,
            'body': {
                'data': f"{response.status_code}",
                'errors': []
            },
        } 
     
    except Exception as e:
        # Unhandled Error Case
        print(f"Exception: {e}")
        return {
            'headers': {
                'Content-Type': 'application/json'
            },
            'statusCode': 500,
            'body': {
                'data': {},
                'errors': [{"message": f"{e}"}],
            },
        }
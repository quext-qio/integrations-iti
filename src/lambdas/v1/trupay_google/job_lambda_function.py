import json, requests
from datetime import datetime
from configuration.config import trupay_config
from qoops_logger import Logger

# Create Logger instance
logger = Logger().instance(f"(ITI) TruPay Google Lambda")

# ----------------------------------------------------------------------------------------
def lambda_handler(event, context):
    now = datetime.now()
    logger.info(f"TruPay Google Lambda Function: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Get token from TruPay Login API
    jwt = get_trupay_token()

    # Get all users information from TruPay API
    trupay_users = get_trupay_users(jwt)

    # Get all users information from Google API
    google_users = get_google_users()

    # Loop through all users on TruPay API and check if they exist on Google API
    for trupay_user in trupay_users:
        # Search for user on Google API
        #google_user = next((user for user in google_users if user['email'] == trupay_user['email']), None)
    
        # If user does not exist on Google API, create user on Google API, 
        # else update user on Google API if there are any changes
        # Print information on users that were created or updated on Google API to CloudWatch
        pass


# ----------------------------------------------------------------------------------------
# Get token from TruPay Login API
def get_trupay_token() -> str:
    # Get required config to call TruPay Login API
    api_key = trupay_config['api_key']
    username = trupay_config['username']
    password = trupay_config['password']
    company_short_name = trupay_config['company_short_name']
    trupay_login_url = trupay_config['trupay_login_url']

    # Headers and payload to call TruPay Login API
    headers = {
        'Api-Key': api_key,
        'Content-Type': 'application/json',
    }
    payload = json.dumps({
        "credentials": {
            "username": username,
            "password": password,
            "company": company_short_name,
        }
    })

    # Call TruPay Login API
    response = requests.request(
        "POST", 
        trupay_login_url, 
        headers=headers, 
        data=payload,
    )
    
    # Check if response is not successful to raise an exception
    if response.status_code != 200:
        raise Exception(f"Error calling TruPay Login API: {response.text}")
    else:
        # Get token from TruPay Login API
        logger.info(f"Successfully called TruPay Login API: {response.text}")
        token = response.json()['token']
        return token
# ----------------------------------------------------------------------------------------
# Get all users information from TruPay API
def get_trupay_users(jwt:str) -> list:
    # Get users from TruPay API

    # Map users to Google API format in Object ()
    return []

# ----------------------------------------------------------------------------------------
# Get all users information from Google API
def get_google_users() -> list:
    # Get users from Google API

    # Map users to Google API format in Object ()
    return []

# ----------------------------------------------------------------------------------------
# Create user on Google API
def create_google_user(trupay_user: dict) -> tuple(bool, dict):
    try:
        # Create user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}

# ----------------------------------------------------------------------------------------
# Update user on Google API
def update_google_user(google_user: dict, trupay_user: dict) -> tuple(bool, dict):
    try:
        # Update user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}
# ----------------------------------------------------------------------------------------
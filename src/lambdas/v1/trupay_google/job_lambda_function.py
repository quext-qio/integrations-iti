import json, requests
from datetime import datetime
from qoops_logger import Logger

# Create Logger instance
logger = Logger().instance(f"ITI: TruPay Google Lambda Function")

# ----------------------------------------------------------------------------------------
def lambda_handler(event, context):
    now = datetime.now()
    logger.info(f"TruPay Google Lambda Function: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    # Get all users information from TruPay API
    trupay_users = get_trupay_users()

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
# Get all users information from TruPay API
def get_trupay_users():
    # Get users from TruPay API

    # Map users to Google API format in Object ()
    return []

# ----------------------------------------------------------------------------------------
# Get all users information from Google API
def get_google_users():
    # Get users from Google API

    # Map users to Google API format in Object ()
    return []

# ----------------------------------------------------------------------------------------
# Create user on Google API
def create_google_user(trupay_user):
    try:
        # Create user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}

# ----------------------------------------------------------------------------------------
# Update user on Google API
def update_google_user(google_user, trupay_user):
    try:
        # Update user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}
# ----------------------------------------------------------------------------------------
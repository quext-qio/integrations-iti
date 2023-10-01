import json, requests
from datetime import datetime

def lambda_handler(event, context):
    now = datetime.now()
    print(f"TruPay Google Lambda Function: {now.strftime('%d/%m/%Y %H:%M:%S')}")

    # Get all users information from TruPay API

    # Get all users information from Google API

    # Loop through all users on TruPay API and check if they exist on Google API

    # If user does not exist on Google API, create user on Google API, 
    # else update user on Google API if there are any changes

    # Print information on users that were created or updated on Google API to CloudWatch


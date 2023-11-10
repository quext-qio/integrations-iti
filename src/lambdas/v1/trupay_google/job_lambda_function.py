import json
import requests
from configuration.config import trupay_config
from models.trupay_data import Employee
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) TruPay Google Lambda")

# ----------------------------------------------------------------------------------------
# Lambda Handler
def lambda_handler(event, context):
    logger.info(f"Starting Job TruPay Google")

    # Get required token from TruPay Login API
    jwt = get_trupay_token()

    # Get all users information from TruPay API
    trupay_users = get_trupay_users(jwt)
    active_users: list[Employee] = trupay_users['active_users']
    others_users: list[Employee] = trupay_users['others_users']
    logger.info(
        f"Active Users: {len(active_users)}, Others Users: {len(others_users)}")

    # Get all users information from Google API
    google_users = get_google_users()

    # Loop through all active users on TruPay API and check if they exist on Google API
    for active_user in active_users:
        # TODO: Search for user on Google API
        # google_user = next((user for user in google_users if user['email'] == trupay_user['email']), None)

        # TODO: If user does not exist on Google API, create user on Google API,
        # TODO: else update user on Google API if there are any changes
        # TODO: Print information on users that were created or updated on Google API to CloudWatch
        pass

    # TODO: Create a report with all users that are not active on TruPay API but exist on Google API
    for other_user in others_users:
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

    # Headers and body to call TruPay Login API
    headers = {
        'Api-Key': api_key,
        'Content-Type': 'application/json',
    }
    body = json.dumps({
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
        data=body,
    )

    # Check if response is not successful to raise an exception because we need the token to call TruPay endpoints
    if response.status_code != 200:
        raise Exception(f"Error calling TruPay Login API: {response.text}")
    else:
        # Get token from TruPay Login API
        logger.info(f"Successfully called TruPay Login API: {response.text}")
        token = response.json()['token']
        return token

# ----------------------------------------------------------------------------------------
# Get all users information from TruPay API
def get_trupay_users(jwt: str) -> dict:
    employees: dict = {
        "active_users": [],
        "others_users": [],
    }
    trupay_get_employees_url = trupay_config['trupay_get_employees_url']
    headers = {
        'Accept': 'application/json',
        'Authentication': f'Bearer {jwt}',
    }

    # Call TruPay List Employees API
    response = requests.request(
        "GET",
        trupay_get_employees_url,
        headers=headers,
    )

    # Check if response is not successful to raise an exception because employees are required
    if response.status_code != 200:
        raise Exception(
            f"Error calling TruPay List Employees API: {response.text}")
    else:
        # Map users to TruPayData format in Object (models/trupay_data.py)
        employees = map_trupay_user(data_dict=response.json())

    # Here we going to return a list of employees, could be empty if there is no employees or if there is an error
    return employees

# ----------------------------------------------------------------------------------------
# Map TruPay actives users to list of [Employee]
def map_trupay_user(data_dict: dict) -> dict:
    mapped_active_users: list[Employee] = []
    mapped_others_users: list[Employee] = []
    for emp in data_dict['employees']:
        # Map TruPay user to Employee object
        employee = Employee(
            id=emp['id'],
            employee_id=emp['employee_id'],
            username=emp['username'],
            first_name=emp['first_name'],
            last_name=emp['last_name'],
            status=emp['status'],
            dates=emp['dates'],
        )

        # Employees that are active will be added to mapped_active_users list
        if emp['status'].lower() == "active":
            mapped_active_users.append(employee)
        else:
            # Employees that are not active will be added to mapped_others_users list
            mapped_others_users.append(employee)

    # Information of active and others users
    employees: dict = {
        "active_users": mapped_active_users,
        "others_users": mapped_others_users,
    }

    return employees


# ----------------------------------------------------------------------------------------
# Get all users information from Google API
def get_google_users() -> list:
    # TODO: Authenticate to Google API

    # TODO: Get users from Google API

    # TODO: Map users to Google API format in Object ()
    return []

# ----------------------------------------------------------------------------------------
# Create user on Google API
def create_google_user(trupay_user: dict) -> tuple:
    try:
        # Create user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}

# ----------------------------------------------------------------------------------------
# Update user on Google API
def update_google_user(google_user: dict, trupay_user: dict) -> tuple:
    try:
        # Update user on Google API
        return True, {}
    except Exception as e:
        return False, {"error": str(e)}
# ----------------------------------------------------------------------------------------

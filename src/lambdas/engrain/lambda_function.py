import json
import requests
from datetime import datetime
from contextlib import closing
from utils.newco_database import NewcoDatabase
from config.engrain_job_status import EngrainJob
from config.config import config
from constants.queries import engrain_push_newco_query


def lambda_handler(event, context):
    print("Engrain Lambda Function")
    # Validate if Engrain has permisions for run
    engrain_info = EngrainJob()
    job_should_execute = engrain_info.is_running()
    if not job_should_execute:
        print(f"Engrain Push: The Job is off")
        return

    print(f"Engrain Push: Starting Job")
    current_dateTime = datetime.now()
    engrain_info.last_execution(current_dateTime)
    engrain_info.currently_executing(True)
    list_errors = []


    # Creation of data dynamic
    try:
        # Get Communities
        sql = "SELECT id as propertyId, name FROM properties WHERE disposition_date IS NULL AND `status` <> 'Archive' ORDER BY name;"
        list_properties, code = get_newco_properties_ids(sql)
        list_communities = list_properties["data"]
        if code == 500:
            print(list_properties["errors"][0])
            list_errors.append({"type":"ERROR", "message":f"Newco database returned an unhandled error, it is necesary for creation of data dynamic", "info": {json.dumps(list_properties["errors"][0])}})
            show_errors(list_errors)
            return

        # Get assets
        assets_response = requests.request("GET", "https://api.sightmap.com/v1/assets", headers=get_headers())
        if assets_response.status_code != 200:
            list_errors.append({"type":"ERROR", "message":f"Sightmap: https://api.sightmap.com/v1/assets used to get assets returns status code not equal 200, it is necesary for creation of data dynamic: {assets_response}"})
            show_errors(list_errors)
            return
        assets_dict = json.loads(assets_response.text)
        list_assets = assets_dict["data"]

        # List to save the properties information
        properties_list = []
        
        # Fill the "properties_list" (name, assetId)
        for community in list_communities:
            is_valid_community, asset = check_asset_by_community(community, list_assets)
            if is_valid_community:
                new_item = {
                    "name":community["name"],
                    "assetId":asset["id"],
                    "pricingId":"",
                    "propertyId": f'{community["propertyId"]}', # Number as string
                }
                properties_list.append(new_item)

        print(f"Engrain Push: Properties list: {len(properties_list)}")
        # Fill the "properties_list" (pricingId)
        for item in properties_list:

            # Get pricing of asset
            pricing_url_endpoint = f"https://api.sightmap.com/v1/assets/{item['assetId']}/multifamily/pricing"
            pricing_response = requests.request("GET", pricing_url_endpoint,  headers=get_headers())
            print(f"Engrain Push: Pricing response: {pricing_response.status_code}, pricing_url_endpoint: {pricing_url_endpoint}")
            if pricing_response.status_code == 200:
                pricing_dict = json.loads(pricing_response.text)
                print(f"Engrain Push: Pricing dict: {pricing_dict}")

                # If outgoing returns empty data   
                if len(pricing_dict["data"]) == 0:
                    list_errors.append({"type":"ERROR", "message":f"Sightmap: {pricing_url_endpoint} used to get pricing process returns empty data: {pricing_response}, Item: {item}"})
                else:
                    list_pricing = pricing_dict["data"]
                    for price in list_pricing:
                        if price["type"] == "push":
                            item["pricingId"] = price["id"]

                    # Validate if don't found pricing type (push) to show a warning
                    if item["pricingId"] == "":
                        list_errors.append({"type":"ERROR", "message":f"Price type push not found using this information: {item}"})
            else:
                # If outgoing don't returns 200, will capture the error
                list_errors.append({"type":"ERROR", "message":f"Sightmap: {pricing_url_endpoint} used to get pricing process returns status code not equal to 200: {pricing_response}"})

        print(f"Engrain Push: Properties list with pricing: {len(properties_list)}")
        # Here data dynamic is already generated 
        # now going to execute engrain logic to populate sightmap
        update_engrain(properties_list, list_errors)
        
    except Exception as e:
        # Show errors
        list_errors.append({"type":"ERROR", "message":f"Unhandled error in creation of data dynamic: {e}"})
        show_errors(list_errors)


# ---------------------------------------------------------------------------------------------------  
def show_errors(list_errors):
    index = 1
    info="INFORMATION:"
    warnings="WARNINGS:"
    errors=""
    for error in list_errors:
        if(error["type"] == "ERROR"):
            errors+=f"\n{error['message']}"
        elif(error["type"] == "WARNING"):
            warnings+=f"\n{index}: {error['message']}"
        else:
            info+=f"\n{index}: {error['message']}"
        index+=1

    print(info)
    print(warnings)
    print(f"Errors: {errors}")


# ---------------------------------------------------------------------------------------------------    
def check_asset_by_community(community, list_assets):
    """Method to validate if community has assets
    Args:
        community (dict): this is a community from "[Engrain Push] General Communities" outgoing
        list_assets (list): this is the response of "[Engrain Push] List assets" outgoing
    Returns:
        tuple: (True, asset) if exist else (False, {})
    """
    for asset in list_assets:
        c_name = community["name"].strip().lower() 
        a_name = asset["name"].strip().lower()
        if not "delete" in a_name: 
            if c_name in a_name or c_name == a_name:
                return True, asset
    return False, {}
    
# ---------------------------------------------------------------------------------------------------
def get_newco_properties_ids(sql):
    """Method to get list of properties from newco db
    Args:
        sql (str): Query to get id, name
    Returns:
        tuple(dict, int): data, status code
    """
    try:
        with closing(NewcoDatabase.get_db_session()) as session:
            cursor = session.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            data = []
            for row in result:
                data.append(dict(zip(cursor.column_names, row)))

        response = { "data": data, "errors": [] }
        return response, 200

    except Exception as e:
        response = { "data": [], "errors": [{"message": str(e)}]}
        return response, 500   

# ---------------------------------------------------------------------------------------------------
def update_engrain(properties_list, list_errors):
    # List to save transactions info
    list_transactions=[]
    index = 0

    # Loop every property
    for property_info in properties_list:
        index +=1
        # Call newco db to validate if has data
        parameters = { "newco_property_id": property_info['propertyId'] }  
        response_of_database, code = data_from_newco(engrain_push_newco_query, parameters, property_info)
        if len(response_of_database['data']) == 0:
            list_errors.append({"type":"WARNING", "message":f"Engrain Push ({index}): No Data Returned From Newco DB: item = {property_info}", "info": json.dumps(property_info)})
        else:
            transaction_info = dict()
            transaction_info["assetId"] = f"{property_info['assetId']}"
            transaction_info["pricingId"] = f"{property_info['pricingId']}"
            transaction_info["commit"] = "1"
            transaction_info["transactionId"] = -1
            is_transaction_open = False
            try:
                # Try to open transaction
                transaction_id, errors = get_transaction_id(property_info)
                
                # if can't get the transaction id, save the error
                if transaction_id == -1:
                    list_errors.append(errors)
                else:
                    is_transaction_open = True
                    # Save transaction info to close in second execution
                    transaction_info["transactionId"] = transaction_id
                    list_transactions.append(transaction_info)

                    # Save transaction id in current property to use later
                    property_info['transactionId'] = transaction_id

                    # Post information
                    print(f"Engrain Push ({index}): Property Id: {property_info}, Size of items: {len(response_of_database['data'])}")
                    is_saved = post_transactions(response_of_database['data'], property_info)   
                    print(f"Engrain Push ({index}): Post Data Correct? {is_saved}, item = {property_info}, info: {json.dumps(transaction_info)}")
                    
                    # Close the transaction
                    url_close_transaction = f"https://api.sightmap.com/v1/assets/{property_info['assetId']}/multifamily/pricing/{property_info['pricingId']}/transactions/{transaction_id}/ingest?commit={1}"
                    close_transaction = requests.request("POST", url_close_transaction, headers=get_headers())
                    is_transaction_open = False
                    print(f"Engrain Push ({index}): First Close Transaction: {close_transaction.status_code}, info: {json.dumps(transaction_info)}, item = {property_info}")
                    list_errors.append({"type":"INFO", "message":f"First Close Transaction ({index}): {close_transaction.status_code}, item = {property_info}", "info": json.dumps(transaction_info)})


            except Exception as e:
                # Save exception error
                print(f"Engrain Push: Exception, {e}")
                list_errors.append({"type":"ERROR", "message":f"Unhandled error in Engrain population flow, Error={e}, item = {property_info['name']}", "info": json.dumps(property_info)})
                if is_transaction_open:
                    # Close the transaction if is currently open
                    url_close_transaction = f"https://api.sightmap.com/v1/assets/{property_info['assetId']}/multifamily/pricing/{property_info['pricingId']}/transactions/{transaction_id}/ingest?commit={1}"
                    close_transaction = requests.request("POST", url_close_transaction, headers=get_headers())
                    print(f"Engrain Push ({index}): Close Transaction in Exception: {close_transaction.status_code}, info: {json.dumps(transaction_info)}, item = {property_info}")
                    list_errors.append({"type":"INFO", "message":f"Close Transaction in Exception ({index}): {close_transaction.status_code}, item = {property_info}", "info": json.dumps(transaction_info)})

    # Close all transaction if any is not closed yet
    index = 1
    for transaction in list_transactions:
        url_close_transaction = f"https://api.sightmap.com/v1/assets/{transaction['assetId']}/multifamily/pricing/{transaction['pricingId']}/transactions/{transaction['transactionId']}/ingest?commit={1}"
        close_transaction = requests.request("POST", url_close_transaction, headers=get_headers())
        if close_transaction.status_code > 299 and close_transaction.status_code < 200:
            list_errors.append({"type":"ERROR", "message":f"Closed a transaction with status pendding in second verification, assetId={transaction['assetId']}, pricingId={transaction['pricingId']}", "info": json.dumps(transaction), "response": json.dumps(close_transaction.text)})
        index+=1

    # Update information in singleton state
    engrain_info = EngrainJob()
    engrain_info.currently_executing(False)
    
    # Show logs
    show_errors(list_errors)
    print(f"Engrain Push: Finish Job")


# ---------------------------------------------------------------------------------------------------
def get_headers():
    """Generate headers for the outgoings
    Returns:
        dict: headers
    """
    return {
        'Content-Type': 'application/json',
        'API-Key': config["api_key"]
    }

# ---------------------------------------------------------------------------------------------------
def get_transaction_id(item):
    """Method to extract the transaction id
    Args:
        item (dict): this is the information of every item of zato (key/value) db
    Returns:
        int: if the transaction is ok will be the transaction id number. if not will be -1
    """
    url_transaction_id = f"https://api.sightmap.com/v1/assets/{item['assetId']}/multifamily/pricing/{item['pricingId']}/ingest"
    transaction_url_response = requests.request("POST", url_transaction_id,  headers=get_headers())
    if transaction_url_response.status_code == 202:
        dict_transaction_response = json.loads(transaction_url_response.text)
        url_path = dict_transaction_response['transaction_url']
        transaction_id = url_path.split("/")[-1]
        print(f"Engrain Push: Open Transaction Id: {transaction_id}, URL: {dict_transaction_response['transaction_ingest_url']}")
        return transaction_id, {}
    else:
        print(f"Engrain Push: Transaction pending, code: {transaction_url_response.status_code}, info: {json.dumps(item)}")
        return -1, {"type":"ERROR", "message":f"Engrain Push: Error to get the Transaction Id, {json.loads(transaction_url_response.text)}", "info": json.dumps(item)}

# ---------------------------------------------------------------------------------------------------
def data_from_newco(sql, parameters, item):
    """
    Method to get data from Newco database.
    Args:
        sql (str): This is the query to retrieve data from Newco DB.
        parameters (dict): This dictionary will have the propertyId used in the SQL query.
        item (dict): This is the information of every item of Zato (key/value) DB.
    Returns:
        tuple: Response of the database and code (success = 200, error = 500).
    """
    try:
        with closing(NewcoDatabase.get_db_session()) as session:
            cursor = session.cursor()
            cursor.execute(sql, parameters)
            result = cursor.fetchall()

            data = []
            column_names = cursor.column_names
            for row in result:
                info = dict(zip(column_names, row))
                info['assetId'] = item['assetId']
                info['pricingId'] = item['pricingId']
                data.append(info)

        response = {"data": data, "errors": []}
        return response, 200

    except Exception as e:
        response = {"data": [], "errors": [{"message": str(e)}]}
        return response, 500


# ---------------------------------------------------------------------------------------------------    
def check_integer_value(value):
    """Check if string number can be int
    Args:
        value (str): This should be a number in string format
    Returns:
        Int: The value as Int
        None: If value can't be cast returns None
    """
    try:
        return int(value)
    except Exception:
        return None

# ---------------------------------------------------------------------------------------------------
def post_transactions(data, property_info):
    """Add the transactions data to Engrain
    Args:
        data (list): This is the response of the newco database   
    Returns:
        Bool: True if everything is ok, False if exist an error 
    """
    _body = []
    for row in data:
        item = {
            "unit_number": f"{row['unit_number']}",
            "provider_id": f"{row['provider_id']}",
            "price": row['price'],
            "lease_term":  check_integer_value(row['lease_term']),
            "available_on": None if row['available_on'] == None else row['available_on'].strftime('%Y-%m-%d'),
            "lease_starts_on":  None if row['lease_starts_on'] == None else row['lease_starts_on'].strftime('%Y-%m-%d'),
        }
        _body.append(item)  
    body = json.dumps(_body, default=str)  
    try:
        url_post_transactions = f"https://api.sightmap.com/v1/assets/{property_info['assetId']}/multifamily/pricing/{property_info['pricingId']}/transactions/{property_info['transactionId']}/ingest?commit={0}"
        response = requests.request("POST", url_post_transactions, data=body, headers=get_headers())
        print(f"Engrain Push: Transaction Id {property_info['transactionId']}, Response Code: {response.status_code}, url: {url_post_transactions}")
        return True

    except Exception as e:
        print(f"Engrain Push: Transaction Id, {property_info['transactionId']}, Error: {e}")
        return False

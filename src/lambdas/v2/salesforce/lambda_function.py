import json
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from acl import ACL
from qoops_logger import Logger

# ----------------------------------------------------------------------------------------
# Create Logger instance
logger = Logger().instance(f"(ITI) Salesforce [Lift-off] Lambda")


# version: V2
def lambda_handler(event, context):
    logger.info(f"Executing with event: {event}, context: {context}")
    
    # ---------------------------------------------------------------------------------------------
    # AccessControl
    # ---------------------------------------------------------------------------------------------
    # is_acl_valid, response_acl = ACL.check_permissions(event)
    # if not is_acl_valid:
    #     return response_acl


    # ---------------------------------------------------------------------------------------------
    # Salesforce flow
    # ---------------------------------------------------------------------------------------------
    try:
        # Get config from parameter store to connect to Quext Salesforce
        quext_username = salesforce_config['username']
        quext_password = salesforce_config['password']
        quext_security_token = salesforce_config['security_token']
        
        # Quext Salesforce authentication
        logger.info(f"Authenticating to Quext Salesforce with username: {quext_username}") 
        salesforce = Salesforce(username=quext_username, password=quext_password, security_token=quext_security_token)
        logger.info(f"Successfully authenticated to Salesforce with username: {quext_username}")

        # Query Quext Salesforce for Sales Completed
        logger.info(f"Trying to get Sales Completed from Quext Salesforce") 
        quext_sales_completed_query = "SELECT sum(Total_Units__c) FROM Opportunity where Product_Family__c = 'IoT'  and (not Name like '%test%') and StageName ='Closed Won' group by StageName Having sum(Total_Units__c) > 0"
        quext_sales_completed_query_result = salesforce.query_all(quext_sales_completed_query)
        quext_sales_completed = quext_sales_completed_query_result['records'][0]["expr0"]
        logger.info(f"Successfully got Sales Completed from Quext Salesforce")

        # Query Quext Salesforce for Installs Completed
        logger.info(f"Trying to get Installs Completed from Quext Salesforce")
        installs_completed_query = "select sum(Units__c) from Property__c where IoT__c = true and (not Name like '%test%') and (IoT_Project_Status__c = 'Completed')"
        installs_completed_query2 = "select sum(Number_of_Units_Installed__c) from Property__c where IoT__c = true and (not Name like '%test%') and (IoT_Project_Status__c <> 'Completed')"
        
        installs_completed_query_result = salesforce.query_all(installs_completed_query)
        installs_completed_query_result2 = salesforce.query_all(installs_completed_query2)
        
        aux = installs_completed_query_result2['records'][0]["expr0"] 
        quext_installs_completed = installs_completed_query_result['records'][0]["expr0"] + (0 if aux is None else installs_completed_query_result['records'][0]["expr0"])
        logger.info(f"Successfully got Installs Completed from Quext Salesforce")
        
        # Calculate Homebase Sales and Installs Completed
        hb_sales_completed = 325 + 48 + 75 + 81 + 54 + 54 + 54 + 54 + 57 + 57 + 460 + 68
        hb_installs_completed = 0
        logger.info(f"Successfully got Homebase Liftoff-related sales completed and installs complete from John McNelly Spreadsheet")
        
        # Combine numbers from Quext and Homebase
        total_sales_completed = hb_sales_completed + quext_sales_completed
        total_installs_completed = quext_installs_completed + hb_installs_completed
        

        # TODO: Use Active Letters Of Intent from McNelly Spreadsheet
        quext_active_letters_of_intent_query_result = 5400
        hb_active_letters_of_intent_query_result = 1387
        total_active_letters_of_intent = quext_active_letters_of_intent_query_result + hb_active_letters_of_intent_query_result
        logger.info(f"Successfully got Quext and Homebase Active Letters Of Intent from John McNelly Spreadsheet")

        # Installs Pending
        total_installs_pending = hb_sales_completed + quext_sales_completed - quext_installs_completed - hb_installs_completed
        logger.info(f"Successfully got Installs Pending from arithmetic calculations")

        # plcu = 11117
        plcu = hb_sales_completed + quext_sales_completed

        # etcu = 28296
        hb_preliftoff_units = 17179 
        q_preliftoff_units = 0
        logger.info(f"Successfully got Pre-Liftoff Units from John McNelly Spreadsheet")
        
        etcu = plcu + hb_preliftoff_units + q_preliftoff_units
        logger.info(f"Successfully calculated etcu ({etcu}) as plcu ({plcu}) + hb_preliftoff_units ({hb_preliftoff_units}) + q_preliftoff_units ({q_preliftoff_units})")

        # Data to return
        query_result = {
            "sc": total_sales_completed,
            'ic': total_installs_completed,
            "ali": total_active_letters_of_intent,
            "ip": total_installs_pending,
            "plcu": plcu,
            "etcu": etcu,
        }

        # Case: Success
        logger.info(f"Successfully got data: {query_result}")
        return {
            'statusCode': "200",
            'body': json.dumps({
                'data': query_result,
                'errors': [],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
    
    except Exception as e:
        # Case: Internal Server Error
        logger.error(f"Unhandled exception in [Salesforce flow]: {e}")
        return {
            'statusCode': "500",
            'body': json.dumps({
                'data': {},
                'errors': [str(e)],
            }),
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',  
            },
            'isBase64Encoded': False  
        }
        

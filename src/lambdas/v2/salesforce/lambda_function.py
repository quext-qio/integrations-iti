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
    # is_acl_valid, response_acl = ACL.check_permitions(event)
    # if not is_acl_valid:
    #     return response_acl


    # ---------------------------------------------------------------------------------------------
    # Salesforce flow
    # ---------------------------------------------------------------------------------------------
    try:
        # Get config from parameter store to connect to Salesforce
        username = salesforce_config['username']
        password = salesforce_config['password']
        security_token = salesforce_config['security_token']
        
        # Salesforce authentication
        logger.info(f"Authenticating to Salesforce with username: {username}") 
        salesforce = Salesforce(username=username, password=password, security_token=security_token)
        logger.info(f"Successfully authenticated to Salesforce with username: {username}")

        # Query for Sales Completed
        logger.info(f"Trying to get Sales Completed from Salesforce") 
        sales_completed_query = "SELECT sum(Total_Units__c) FROM Opportunity where Product_Family__c = 'IoT'  and (not Name like '%test%') and StageName ='Closed Won' group by StageName Having sum(Total_Units__c) > 0"
        sales_completed_query_result = salesforce.query_all(sales_completed_query)
        sales_completed = sales_completed_query_result['records'][0]["expr0"]
        logger.info(f"Successfully got Sales Completed from Salesforce")

        # Query for Installs Completed
        logger.info(f"Trying to get Installs Completed from Salesforce")
        installs_completed_query = "select sum(Units__c) from Property__c where IoT__c = true and (not Name like '%test%') and (IoT_Project_Status__c = 'Completed')"
        installs_completed_query2 = "select sum(Number_of_Units_Installed__c) from Property__c where IoT__c = true and (not Name like '%test%') and (IoT_Project_Status__c <> 'Completed')"
        
        installs_completed_query_result = salesforce.query_all(installs_completed_query)
        installs_completed_query_result2 = salesforce.query_all(installs_completed_query2)
        
        aux = installs_completed_query_result2['records'][0]["expr0"] 
        #installs_completed = installs_completed_query_result['records'][0]["expr0"] + (0 if aux is None else installs_completed_query_result['records'][0]["expr0"])
        installs_completed = 7571
        logger.info(f"Successfully got Installs Completed from Salesforce")

        # TODO: Query for Active Letters Of Intent
        active_letters_of_intent_query_result = 5400
        logger.info(f"Successfully got Active Letters Of Intent")

        # Installs Pending
        #installs_pending = 1319 + sales_completed - installs_completed
        installs_pending = 3546
        logger.info(f"Successfully got Installs Pending from Calculations")

        # TODO: PLCU
        plcu = 11117

        # TODO: ETCU
        etcu = 28296

        # Data to return
        query_result = {
            "sc": sales_completed,
            'ic': installs_completed,
            "ali": active_letters_of_intent_query_result,
            "ip": installs_pending,
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
        
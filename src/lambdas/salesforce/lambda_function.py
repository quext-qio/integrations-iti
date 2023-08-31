import json
from global_config.config import salesforce_config
from simple_salesforce import Salesforce
from acl import ACL

def lambda_handler(event, context):
    print(f"Event: {event}, context: {context}")
    
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
        salesforce = Salesforce(username=username, password=password, security_token=security_token)
        
        # Query for Sales Completed
        sales_completed_query = "SELECT sum(Total_Units__c) FROM Opportunity where Product_Family__c = 'IoT'  and (not Name like '%test%') and StageName ='Closed Won' group by StageName Having sum(Total_Units__c) > 0"
        sales_completed_query_result = salesforce.query_all(sales_completed_query)

        # Query for Installs Completed
        installs_completed_query = "select sum(Units__c) from Property__c where IoT__c = true and (not Name like '%test%') and (IoT_Project_Status__c = 'Completed')"
        installs_completed_query_result = salesforce.query_all(installs_completed_query)

        # TODO: Query for Active Letters Of Intent
        active_letters_of_intent_query = ""
        active_letters_of_intent_query_result = 9500

        # Data to return
        query_result = {
            "sc": sales_completed_query_result['records'][0]["expr0"],
            'ic': installs_completed_query_result['records'][0]["expr0"],
            "ali": active_letters_of_intent_query_result,
        }


        # Case: Success
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
        print(f"Unhandled exception in [Salesforce flow]: {e}")
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
        
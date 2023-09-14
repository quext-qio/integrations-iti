import json
import threading
from datetime import date, datetime, timedelta
from configuration.config import jira_config
from core.jira_automation import JiraAutomation
from schemas.request_body_post import RequestBodyPost

lock = threading.Lock()

def lambda_handler(event, context):
    print(f"Jira handler: {event}")
    try:
        with lock:
            #input = event
            input = json.loads(event['Records'][0]['body'])
            # Validate input from user
            is_valid, input_errors = RequestBodyPost(input).is_valid()
            if is_valid:
            
                # Get Inputs from user
                labels = [x.replace(" ", "-") for x in input['labels']]
                issue_type= input['issue_type']
                project_name=input['project_name']
                ticket_summary =  input['ticket_summary']
                ticket_description = input['ticket_description']
                list_issues = input['list_issues']
                priority = input['priority']
                testing = True if "testing" in input and "True" == input['testing'] else False
                print("JIRA Parameters ready")

                # Create instance of jira class
                jira = JiraAutomation(
                    project_name=project_name, 
                    server_url=jira_config["server_url"], 
                    reporter_email=jira_config["reporter_email"], 
                    token=jira_config["token"]
                )
                print("JIRA Instance ready")
                
                # Create ticket with information
                ticket, is_new = jira.generate_ticket(
                    summary=ticket_summary, 
                    description=ticket_description, 
                    list_issues=list_issues, 
                    priority=priority, 
                    labels=labels, 
                    issue_type=issue_type, 
                    testing=testing,
                )
                print(f"JIRA ticket: {ticket}")
                
                # Success case
                return {
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'statusCode': 201 if is_new else 200,
                    'body': {
                        'data': {
                            'ticket' : f"{ticket}", 
                            'is_new': f"{is_new}"
                        },
                        'errors': []
                    },
                }
            else:
                # Bad request Case
                errors = [{"message": f"{k}, {v[0]}" } for k,v in input_errors.items()]
                print(f"Bad request Case, Errors: {errors}")
                return {
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'statusCode': 400,
                    'body': {
                        'data': {},
                        'errors': errors
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
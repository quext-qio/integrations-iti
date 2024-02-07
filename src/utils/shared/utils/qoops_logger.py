import logging
import inspect
import json
import requests
import os

# ----------------------------------------------------------------------------
# This class is used to handle errors and critical issues
# Important: It is used to override a logger but should not be used directly
class _QoopsLogger(logging.Logger):
    """
    Class to get information about errors ans critical issues
    """
    custom_domain_name = os.environ['CUSTOM_DOMAIN_NAME']
    stage = os.environ['CURRENT_ENV']
    url = f"https://{custom_domain_name}/api/v2/jira/qoops"
    headers = {'Content-Type': 'application/json'}

    def __init__(self, name=inspect.stack()[1][3], level=logging.DEBUG):
        return super(_QoopsLogger, self).__init__(name, level)

    # Method to handle errors
    def error(self, msg, *args, **kwargs):
        # Error case:
        print(f"\nGenerating ticket: {msg}: {self.name} - Environment {self.stage}")
        payload = self.create_payload(
            msg,
            issue_type="Bug",
            priority=3,
            project_name="QIN",
        )
        information_detail = self.call_jira_endpoint(msg, payload)
        return super(_QoopsLogger, self).error(information_detail, *args, **kwargs)

    # Method to handle critical issues
    def critical(self, msg, *args, **kwargs):
        # Critical case:
        print(f"\nGenerating ticket: {msg}: {self.name} - Environment {self.stage}")
        payload = self.create_payload(
            msg,
            issue_type="Bug",
            priority=5,
            project_name="QIN",
        )
        information_detail = self.call_jira_endpoint(msg, payload)
        return super(_QoopsLogger, self).critical(information_detail, *args, **kwargs)

    # Create payload for jira required input
    def create_payload(
        self,
        msg,
        issue_type="Bug",
        priority=3,
        project_name="QIN",
    ):
        payload = json.dumps({
            "project_name": project_name,
            "ticket_summary": f"Issue in Service {self.name} - Environment {self.stage}",
            "ticket_description": f"Ticket is automatically generated for issues found in {self.name}",
            "issue_type": issue_type,
            "priority": priority,
            "labels": ["Qoops", f"{self.name}-{self.stage}", "Jira-Automation", "ITI-Service"],
            "list_issues": [msg],
            "testing": "true"
        })
        return payload

    # Method to report issues
    def call_jira_endpoint(self, msg, payload):
        information_detail = f"{msg}."
        try:
            response = requests.request(
                "POST",
                self.url,
                headers=self.headers,
                data=payload,
            )

            # If get success response from Jira SQS, will add SQS response log detail
            if response.status_code == 200:
                data = json.loads(response.text)
                information_detail = information_detail + f" SQS Response {data}"
            return information_detail
        except Exception as e:
            print(f"Error Calling Qoops Endpoint: {str(e)}")
            information_detail = information_detail + f" SQS Error {str(e)}"
            return information_detail


# ----------------------------------------------------------------------------
# This class is used to create logger instance
# If you need to create a logger, please use this class
# ----------------------------------------------------------------------------
class Logger():
    """
    Class to allow logic for creation of log and report issues
    """
    
    def instance(self, service_name, level=logging.INFO):
        # Set custom class to handle error and critical issues
        logging.setLoggerClass(_QoopsLogger)

        # Get logger by service name  
        logger = logging.getLogger(f"{service_name}")
        logger.setLevel(logging.INFO)

        # Create CloudWatch logs handler
        cloudwatch_handler = logging.StreamHandler()
        cloudwatch_handler.setLevel(level)

        # Create formatter
        formatter = logging.Formatter('[AUTOMATION_LOG] "Date": %(asctime)s - "Level": %(levelname)s - "Name": %(name)s - "Message": %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

        # Set formatter in file and console
        cloudwatch_handler.setFormatter(formatter)

        # Add the handlers to logger
        logger.addHandler(cloudwatch_handler)
        
        return logger
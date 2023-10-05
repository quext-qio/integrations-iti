import os, json, boto3
from aws_cdk import NestedStack
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment

class EnvStack(NestedStack):
    @property
    def get_env(self):
        return self.env

    def __init__(self, scope: Construct, construct_id: str, app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Get name of the parameter store associated with the stage
        parameter_name = app_environment.get_parameter_store_name()

        # Load session using default AWS credentials
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token=os.getenv('AWS_SESSION_TOKEN')

        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
        )
        
        # Create a client to interact with the STS (Security Token Service)
        sts_client = session.client("sts")

        role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')
        
        # Assume the IAM role
        assume_role = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"{app_environment.get_stage_name()}-assumed-session"
        )

        # Extract the temporary credentials from the assume_role
        credentials = assume_role['Credentials']

        # Create a new session using the temporary credentials
        new_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )
        
        # Get the environmet values from Parameter Store using the assumed session
        ssm_client = new_session.client(
            "ssm", 
            region_name="us-east-1", 
        )
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        all_params = json.loads(response["Parameter"]["Value"])


        # --------------------------------------------------------------------
        # Create a dict with the environment variables depending of integration
        stage_name = app_environment.get_stage_name()
        
        environment_dict = {
            "placepay": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "PLACE_PAY_API_KEY": all_params["PLACE_PAY_API_KEY"],
                "ACL_HOST": all_params["ACL_HOST"],
            },
            "guestcards": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                # Realpage
                "WS_REALPAGE_ILM_APIKEY": all_params["WS_REALPAGE_ILM_APIKEY"],
                "DH_REALPAGE_ILM_APIKEY": all_params["DH_REALPAGE_ILM_APIKEY"],
                "WS_REALPAGE_L2L_APIKEY": all_params["WS_REALPAGE_L2L_APIKEY"],
                "DH_REALPAGE_L2L_APIKEY": all_params["DH_REALPAGE_L2L_APIKEY"],
                # Spherexx
                "SPHEREXX_USERNAME": all_params["SPHEREXX_USERNAME"],
                "SPHEREXX_PASSWORD": all_params["SPHEREXX_PASSWORD"],
                # Yardi
                "YARDI_USER_NAME": all_params["YARDI_USER_NAME"],
                "YARDI_PASSWORD": all_params["YARDI_PASSWORD"],
                "YARDI_SERVER_NAME": all_params["YARDI_SERVER_NAME"],
                "YARDI_DATABASE": all_params["YARDI_DATABASE"],
                "YARDI_INTERFACE_LICENSE": all_params["YARDI_INTERFACE_LICENSE"],
                "LEASING_HOST": all_params["LEASING_HOST"],
                "IPS_HOST": all_params["IPS_HOST"],
                "YARDI_URL": all_params["YARDI_URL"],
                # Resman
                "RESMAN_INTEGRATION_PARTNER_ID": all_params["RESMAN_INTEGRATION_PARTNER_ID"],
                "RESMAN_ACCOUNT_ID": all_params["RESMAN_ACCOUNT_ID"],
                "RESMAN_PROPERTY_ID": all_params["RESMAN_PROPERTY_ID"],
                "RESMAN_API_KEY": all_params["RESMAN_API_KEY"],
                "QXT_CALENDAR_TOUR_HOST": all_params["QXT_CALENDAR_TOUR_HOST"],
                #Funnel
                "FUNNEL_API_KEY": all_params["FUNNEL_API_KEY"],
            },
            "transunion": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                # Identity
                "TRANSUNION_IDENTITY_HOST": all_params["TRANSUNION_IDENTITY_HOST"],
                "TRANSUNION_AUTHENTICATION": all_params["TRANSUNION_AUTHENTICATION"],
                "TRANSUNION_PROPERTY_ID_CODE": all_params["TRANSUNION_PROPERTY_ID_CODE"],
                "TRANSUNION_SECRET_KEY": all_params["TRANSUNION_SECRET_KEY"],
                # Screening
                "TRANSUNION_MEMBER_NAME": all_params["TRANSUNION_MEMBER_NAME"],
                "TRANSUNION_REPORT_PASSWORD": all_params["TRANSUNION_REPORT_PASSWORD"],
                "TRANSUNION_PROPERTY_ID": all_params["TRANSUNION_PROPERTY_ID"],
                "TRANSUNION_SOURCE_ID": all_params["TRANSUNION_SOURCE_ID"],
                "TRANSUNION_POST_BACK_URL": all_params["TRANSUNION_POST_BACK_URL"],
                "TRANSUNION_REPORT_HOST": all_params["TRANSUNION_REPORT_HOST"],
                # Postback
                "LEASING_HOST": all_params["LEASING_HOST"],
                "LEASING_BACKGROUND_SCREENING_ENDPOINT": all_params["LEASING_BACKGROUND_SCREENING_ENDPOINT"],
                "LEASING_FIND_BY_NUMBER": all_params["LEASING_FIND_BY_NUMBER"],
            },
            "units": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "RESMAN_INTEGRATION_PARTNER_ID": all_params["RESMAN_INTEGRATION_PARTNER_ID"],
                "RESMAN_API_KEY": all_params["RESMAN_API_KEY"],
                "NEWCO_DB_HOST": all_params["NEWCO_DB_HOST"],
                "NEWCO_DB_PASSWORD": all_params["NEWCO_DB_PASSWORD"],
                "NEWCO_DB_NAME": all_params["NEWCO_DB_NAME"],
                "NEWCO_DB_USER": all_params["NEWCO_DB_USER"],
                "ENGRAIN_HOST": all_params["ENGRAIN_HOST"],
                "ENGRAIN_API_KEY": all_params["ENGRAIN_API_KEY"],
            },
            "communities": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "AUTH_HOST": all_params["AUTH_HOST"],
            },
            "customers": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "AUTH_HOST": all_params["AUTH_HOST"],
            },
            "residents": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "NEWCO_DB_HOST": all_params["NEWCO_DB_HOST"],
                "NEWCO_DB_PASSWORD": all_params["NEWCO_DB_PASSWORD"],
                "NEWCO_DB_NAME": all_params["NEWCO_DB_NAME"],
                "NEWCO_DB_USER": all_params["NEWCO_DB_USER"],
            },
            "engrain": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "ENGRAIN_API_KEY": all_params["ENGRAIN_API_KEY"],
                "ENGRAIN_QUEXT_API_KEY": all_params["ENGRAIN_QUEXT_API_KEY"],
                "ENGRAIN_MADERA_UUID": all_params["ENGRAIN_MADERA_UUID"],
                "NEWCO_DB_HOST": all_params["NEWCO_DB_HOST"],
                "NEWCO_DB_PASSWORD": all_params["NEWCO_DB_PASSWORD"],
                "NEWCO_DB_NAME": all_params["NEWCO_DB_NAME"],
                "NEWCO_DB_USER": all_params["NEWCO_DB_USER"],
            },
            "touravailability": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "FUNNEL_API_KEY": all_params["FUNNEL_API_KEY"],
                "QXT_CALENDAR_TOUR_HOST": all_params["QXT_CALENDAR_TOUR_HOST"],
                "IPS_HOST": all_params["IPS_HOST"],
                "WS_REALPAGE_ILM_APIKEY": all_params["WS_REALPAGE_ILM_APIKEY"],
                "DH_REALPAGE_ILM_APIKEY": all_params["DH_REALPAGE_ILM_APIKEY"],
                "WS_REALPAGE_L2L_APIKEY": all_params["WS_REALPAGE_L2L_APIKEY"],
                "DH_REALPAGE_L2L_APIKEY": all_params["DH_REALPAGE_L2L_APIKEY"],
                "LICENSE_KEY" : all_params["LICENSE_KEY"]
            },
            "conservice": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "IPS_HOST": all_params["IPS_HOST"],
            },
            "salesforce": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "SALESFORCE_USERNAME": all_params["SALESFORCE_USERNAME"],
                "SALESFORCE_PASSWORD": all_params["SALESFORCE_PASSWORD"],
                "SALESFORCE_SECURITY_TOKEN": all_params["SALESFORCE_SECURITY_TOKEN"],
            },
            "qoops": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "JIRA_REPORTER_TOKEN": all_params["JIRA_REPORTER_TOKEN"],
            },
            "onetimelink": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "IPS_HOST": all_params["IPS_HOST"],
            },
            "rentdynamics": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
                "IPS_HOST": all_params["IPS_HOST"],
                # Newco
                "NEWCO_DB_HOST": all_params["NEWCO_DB_HOST"],
                "NEWCO_DB_PASSWORD": all_params["NEWCO_DB_PASSWORD"],
                "NEWCO_DB_NAME": all_params["NEWCO_DB_NAME"],
                "NEWCO_DB_USER": all_params["NEWCO_DB_USER"],
            },
            "trupay-google": {
                "STAGE": stage_name,
                "CURRENT_ENV": all_params["CURRENT_ENV"],
                "ACL_HOST": all_params["ACL_HOST"],
            },
        }

        self.env = environment_dict
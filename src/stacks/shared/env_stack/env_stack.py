import os
import boto3
from aws_cdk import NestedStack
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment

class EnvStack(NestedStack):
    @property
    def get_env(self):
        return self.env
    
    @property
    def get_assume_role(self):
        return self.assume_role

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
        self.assume_role = assume_role

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

        self.env = {
            "parameter_store": response["Parameter"]["Value"]
        }
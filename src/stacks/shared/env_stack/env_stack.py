from aws_cdk import (
    Stack
)
import boto3
import os
from constructs import Construct
from src.utils.enums.stage_name import StageName

class EnvStack(Stack):
    @property
    def get_env(self):
        return self.env

    def __init__(self, scope: Construct, construct_id: str, stage_name: StageName, role_arn: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Create the environment based on the stage name
        parameter_name = ""
        if stage_name == StageName.DEV:
            parameter_name = "/dev/integrations/aws/migration" 
        elif stage_name == StageName.STAGE:
            parameter_name = "/stage/integrations/aws/migration"
        elif stage_name == StageName.PROD:
            parameter_name = "/prod/integrations/aws/migration"
        else:
            raise Exception("Invalid stage name")

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
        
        # Assume the IAM role
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"{stage_name.value}-assumed-session"
        )

        # Extract the temporary credentials from the response
        credentials = response['Credentials']

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
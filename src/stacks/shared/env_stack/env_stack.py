from aws_cdk import (
    Stack
)
import boto3
from constructs import Construct
from src.utils.enums.stage_name import StageName

class EnvStack(Stack):
    @property
    def get_env(self):
        return self.env

    def __init__(self, scope: Construct, construct_id: str, stage_name: StageName, **kwargs) -> None:
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
        session = boto3.Session(profile_name='default')
        
        # Create a client to interact with the STS (Security Token Service)
        sts_client = session.client("sts")
        
        # Assume the IAM role
        response = sts_client.assume_role(
            RoleArn="arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters",
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
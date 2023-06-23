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
        # TODO: Change the parameter name when all environments are ready
        parameter_name = ""
        if stage_name == StageName.DEV:
            parameter_name = "/integrations/dev/backend" 
        elif stage_name == StageName.STAGE:
            parameter_name = "/integrations/stage/backend"
        elif stage_name == StageName.PROD:
            parameter_name = "/integrations/aws/migration"
        else:
            raise Exception("Invalid stage name")

        ssm_client = boto3.client("ssm", region_name="us-east-1")
        response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)

        self.env = {
            "parameter_store": response["Parameter"]["Value"]
        }
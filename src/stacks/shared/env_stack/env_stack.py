from aws_cdk import (
    Stack,
    aws_ssm as ssm
)
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
            parameter_name = "/integrations/aws/migration" 
        elif stage_name == StageName.STAGE:
            parameter_name = "/integrations/aws/migration"
        elif stage_name == StageName.PROD:
            parameter_name = "/integrations/aws/migration"
        else:
            raise Exception("Invalid stage name")
        
        self.env = {
            "parameter_store": ssm.StringParameter.from_string_parameter_attributes(self, "parameter_store", parameter_name=parameter_name).string_value
        }
    
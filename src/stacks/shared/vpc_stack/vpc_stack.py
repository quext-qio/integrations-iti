from constructs import Construct
from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2_,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    Duration,
)
from src.utils.enums.app_environment import AppEnvironment

class VpcStack(NestedStack):
    @property
    def get_vpc(self):
        return self.vpc
    
    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        #TODO: Read id from app_environment
        vpc_id = "vpc-02ef368fcc88d90de"
        # Get VPC by id
        vpc = ec2_.Vpc.from_lookup(
            self, f"{app_environment.get_stage_name()}-iti-vpc", 
            vpc_id=vpc_id,
            #is_default=True,
            #vpc_name=f"{app_environment.get_stage_name()}-iti-vpc"
        )


        # --------------------------------------------------------------------
        # Create lambda function instance test VPC 
        lambda_function = lambda_.Function(
            self, 
            f"{app_environment.get_stage_name()}-vpc-lambda",
            description="This Lambda is responsible to test VPC", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=Duration.seconds(30),
            code=lambda_.Code.from_asset("./src/lambdas/v1/vpc"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-vpc-lambda",
            vpc=vpc,
        )

        self.vpc = vpc
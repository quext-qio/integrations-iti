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
        
        # vpc = ec2_.Vpc(
        #     self, f"{app_environment.get_stage_name()}-iti-vpc",
        #     vpc_name=f"{app_environment.get_stage_name()}-iti-vpc",
        #     max_azs=2,
        #     nat_gateways=2,
        #     ip_addresses=ec2_.IpAddresses.cidr("10.0.0.0/16"),
        #     subnet_configuration=[
        #         ec2_.SubnetConfiguration(
        #             name="Public",
        #             subnet_type=ec2_.SubnetType.PUBLIC,
        #             cidr_mask=24
        #         ), 
        #         ec2_.SubnetConfiguration(
        #             name="Private",
        #             subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS,
        #             cidr_mask=24
        #         ), 
        #         # ec2_.SubnetConfiguration(
        #         #     subnet_type=ec2_.SubnetType.PRIVATE_ISOLATED,
        #         #     name="Private",
        #         #     cidr_mask=24
        #         # )
        #     ],
        #     nat_gateway_provider=ec2_.NatProvider.gateway(),
        # )

        # --------------------------------------------------------------------
        #TODO: Read id from app_environment
        vpc_id = "vpc-02ef368fcc88d90de"
        # Get VPC by id
        vpc = ec2_.Vpc.from_lookup(
            self, f"{app_environment.get_stage_name()}-iti-vpc", 
            vpc_id=vpc_id,
            vpc_name=f"{app_environment.get_stage_name()}-iti-vpc"
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
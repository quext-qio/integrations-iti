from constructs import Construct
from aws_cdk import (
    NestedStack,
    aws_ec2 as ec2_,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    Duration,
    aws_iam as iam_,
    Fn,
)
from src.utils.enums.app_environment import AppEnvironment


class VpcStack(NestedStack):
    @property
    def vpc(self) -> ec2_.Vpc:
        return self._vpc
    
    @property
    def vpc_subnets(self) -> ec2_.SubnetSelection:
        return self._vpc_subnets
    
    @property
    def security_groups(self) -> list[ec2_.SecurityGroup]:
        return self._security_groups

    def __init__(self, scope: Construct, construct_id: str, layers: list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Read VPC by id
        vpc_id = app_environment.get_vpc_id()
        vpc = ec2_.Vpc.from_lookup(
            self, f"{app_environment.get_stage_name()}-iti-vpc",
            vpc_id=vpc_id,
        )
        self._vpc = vpc
        print(f"""
        VPC found: {vpc.vpc_id}    
        """)

        # --------------------------------------------------------------------
        # Subnet selection
        private_subnets = vpc.select_subnets(subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS)
        subnet_ids = []
        if len(private_subnets.subnets) == 0:
            raise Exception(
                "VPC Private subnet not found [PRIVATE_WITH_EGRESS]")
        else:
            print(f"VPC [PRIVATE_WITH_EGRESS]: {len(private_subnets.subnets)}")
            for subnet in private_subnets.subnets:
                subnet_ids.append(subnet.subnet_id)
                print(f"Subnet ID: {subnet.subnet_id}")

        vpc_subnets = ec2_.SubnetSelection(
            subnet_filters=[
                ec2_.SubnetFilter.by_ids(
                    subnet_ids=subnet_ids
                )
            ]
        )
        self._vpc_subnets = vpc_subnets

        # --------------------------------------------------------------------
        # TODO: Read Security Group by id
        security_group_id = app_environment.get_security_group_id()
        security_group = ec2_.SecurityGroup.from_security_group_id(
            self, f"{app_environment.get_stage_name()}-iti-security-group",
            security_group_id=security_group_id,
        )
        self._security_groups = [security_group]

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
            vpc_subnets=vpc_subnets,
            security_groups=[security_group],
        )

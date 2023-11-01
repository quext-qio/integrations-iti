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
    def __init__(self, scope: Construct, construct_id: str, layers:list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Read VPC by id
        vpc_id = app_environment.get_vpc_id()
        vpc = ec2_.Vpc.from_lookup(
            self, f"{app_environment.get_stage_name()}-iti-vpc", 
            vpc_id=vpc_id,
        )
        self.vpc = vpc
        print(f"""
        VPC found: {vpc.vpc_id}    
        """)

        # --------------------------------------------------------------------
        private_subnets = vpc.select_subnets(subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS)
        if len(private_subnets.subnets) == 0:
            raise Exception("VPC Private subnet not found [PRIVATE_WITH_EGRESS]")
        else:
            print(f"VPC [PRIVATE_WITH_EGRESS]: {len(private_subnets.subnets)}")
            for subnet in private_subnets.subnets:
                print(f"VPC Private subnet ID: {subnet.subnet_id}")
            


        # --------------------------------------------------------------------
        # TODO: Read Security Group by id
        security_group_id = app_environment.get_security_group_id()
        security_group = ec2_.SecurityGroup.from_security_group_id(
            self, f"{app_environment.get_stage_name()}-iti-security-group", 
            security_group_id=security_group_id,
        )

            #allow_all_outbound=True,
            #mutable=False,
            #allow_all_ipv6_outbound=True,

        # security_group.add_ingress_rule(
        #     peer=ec2_.Peer.any_ipv4(),
        #     connection=ec2_.Port.all_traffic()
        # )
        self.security_group = security_group


        
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
            vpc_subnets=ec2_.SubnetSelection(
                subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS,
            ),
            security_groups=[security_group],
            role=iam_.Role.from_role_arn(
                self, f"{app_environment.get_stage_name()}-vpc-lambda-role",
                role_arn='arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters',                          
            )
        )
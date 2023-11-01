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
    
    @property
    def get_security_group(self):
        return self.security_group
    
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
            VPC: {vpc}
        """)

        # --------------------------------------------------------------------
        private_subnets = vpc.select_subnets(subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS)
        print(f"""
            VPC Subnet: {private_subnets}
        """)
        if len(private_subnets.subnets) == 0:
            raise Exception("VPC Private subnet not found [PRIVATE_WITH_EGRESS]")
        else:
            print(f"VPC Private subnet found [PRIVATE_WITH_EGRESS]: {len(private_subnets.subnets)}")
            for subnet in private_subnets.subnets:
                print(f"VPC Private subnet: {subnet.internet_connectivity_established}")
            


        # --------------------------------------------------------------------
        # Read Security Group by id
        # security_group_id = app_environment.get_security_group_id()
        # security_group = ec2_.SecurityGroup.from_security_group_id(
        #     self, 
        #     id=f"{app_environment.get_stage_name()}-iti-security-group", 
        #     security_group_id=security_group_id,
        #     #mutable=False,
        # )
        # self.security_group = security_group

        security_group = ec2_.SecurityGroup(
            self, f"{app_environment.get_stage_name()}-iti-security-group", 
            vpc=vpc,
        )
        security_group.add_ingress_rule(
            peer=ec2_.Peer.any_ipv4(),
            connection=ec2_.Port.all_traffic()
        )
        self.security_group


        # --------------------------------------------------------------------
        # Subnet selection [Private with Egress]
        vpc_subnets = ec2_.SubnetSelection(
            subnet_type=ec2_.SubnetType.PRIVATE_WITH_EGRESS,
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
            security_groups=[security_group],
            vpc_subnets=vpc_subnets,
        )
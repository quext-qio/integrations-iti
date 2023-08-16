import os
import boto3
from constructs import Construct
from src.utils.enums.stage_name import StageName
from aws_cdk import (
    NestedStack,
    aws_apigateway as apigateway_,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_certificatemanager as acm_,
    aws_iam as iam_,
    aws_route53 as route53_,
    aws_route53_targets as route53targets_,
    CfnOutput,
)

# Lambda function to store the API URL after deployment
def print_api_url_lambda(scope: Construct, api_url: str, stage: StageName):
    return lambda_.Function(
        scope,
        f"{stage.name}-ApiUrlFunction",
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_inline(
            "import os\n"
            "def handler(event, context):\n"
            f"    print('API URL for Aws Integration Engine in stage ({stage.name}):', '{api_url}')"
        ),
    )


class APIStack(NestedStack):
    @property
    def get_api(self):
        return self.api
    
    @property
    def get_resources(self):
        return self.resources


    def __init__(self, scope: Construct, construct_id: str, stage: StageName, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --------------------------------------------------------------------
        # --------------------------------------------------------------------
        # Test custom domain
        domain_name = "d-kept97rbkf.execute-api.us-east-1.amazonaws.com"
        hosted_zone_id = "Z1UJRXOUMOOFQ8"
        certificate_arn = "arn:aws:acm:us-east-1:633546161654:certificate/eb1794a2-4724-475a-9aad-b9e5bdaa38e3"
        
        role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')
        assumed_session = self.assume_role(role_arn, stage)
        acm_client = assumed_session.client('acm', region_name='us-east-1')
        certificate = acm_.Certificate.from_certificate_arn(self, "MyCertificate", certificate_arn)
        
        # custom_domain = self.api.add_domain_name("CustomDomain",
        #     domain_name=domain_name,
        #     certificate=certificate,
        #     endpoint_type=apigateway_.EndpointType.REGIONAL,
        #     security_policy=apigateway_.SecurityPolicy.TLS_1_2
        # )

        # hosted_zone = route53_.HostedZone.from_hosted_zone_attributes(self, "HostedZone",
        #     hosted_zone_id=hosted_zone_id,
        #     zone_name="integrations-api.dev.quext.io"
        # )

        # route53_.ARecord(self, "ApiGatewayAliasRecord",
        #     target=route53_.RecordTarget.from_alias(route53targets_.ApiGatewayDomain(custom_domain)),
        #     zone=hosted_zone
        # )

        # CfnOutput(self, "ApiUrl",
        #     value=custom_domain.domain_name + "/{proxy+}",
        #     description="URL of the API with custom domain"
        # )


        # --------------------------------------------------------------------
        # Create a Rest API instance
        self.api = apigateway_.RestApi(
            self, "Integrations_Api", 
            rest_api_name="Integrations_Api", 
            description="Base API Gateway for Zato to AWS Migration",
            deploy=True,
            deploy_options=apigateway_.StageOptions(
                stage_name=stage.value, 
                logging_level=apigateway_.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True,
                tracing_enabled=True,
            ),
            endpoint_configuration=apigateway_.EndpointConfiguration(
                types=[apigateway_.EndpointType.REGIONAL],
            ),
        )
        # --------------------------------------------------------------------
        custom_domain_name = apigateway_.DomainName.from_domain_name_attributes(self, "DomainName",
            domain_name=domain_name,
            domain_name_alias_hosted_zone_id=hosted_zone_id,
            domain_name_alias_target=domain_name
        )

        apigateway_.BasePathMapping(self, "BasePathMapping",
            domain_name=custom_domain_name,
            rest_api=self.api
        )

        # --------------------------------------------------------------------

        # Standard root resource
        api_resource = self.api.root.add_resource("api")

        # Current supported versions
        api_v1 = api_resource.add_resource("v1")
        api_v2 = api_resource.add_resource("v2")

        # Suported third party services v1
        placepay_resource_v1 = api_v1.add_resource("placepay")
        resman_resource_v1 = api_v1.add_resource("resman")
        transunion_resource_v1 = api_v1.add_resource("transunion")
        general_resource_v1 = api_v1.add_resource("general")
        engrain_resource_v1 = api_v1.add_resource("engrain")
        tour_resource_v1 = api_v1.add_resource("tour")
        salesforce_resource_v1 = api_v1.add_resource("salesforce")

        # Create a dictionary of all the resources of v1
        dict_v1 = {
            "placepay": placepay_resource_v1,
            "resman": resman_resource_v1,
            "transunion": transunion_resource_v1,
            "general": general_resource_v1,
            "engrain": engrain_resource_v1,
            "tour": tour_resource_v1,
            "salesforce": salesforce_resource_v1,
        }

        # Suported third party services v2
        placepay_resource_v2 = api_v2.add_resource("placepay")
        resman_resource_v2 = api_v2.add_resource("resman")
        transunion_resource_v2 = api_v2.add_resource("transunion")
        general_resource_v2 = api_v2.add_resource("general")
        engrain_resource_v2 = api_v2.add_resource("engrain")
        tour_resource_v2 = api_v2.add_resource("tour")
        salesforce_resource_v2 = api_v2.add_resource("salesforce")

        # Create a dictionary of all the resources of v2
        dict_v2 = {
            "placepay": placepay_resource_v2,
            "resman": resman_resource_v2,
            "transunion": transunion_resource_v2,
            "general": general_resource_v2,
            "engrain": engrain_resource_v2,
            "tour": tour_resource_v2,
            "salesforce": salesforce_resource_v2,
        }

        # Create a dictionary of all the resources and versions
        self.resources = {
            "v1": dict_v1,
            "v2": dict_v2,
        }

        # # --------------------------------------------------------------------
        # # Assume the IAM role
        # role_arn = os.getenv('ROLE_ARN', 'arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters')
        # assumed_session = self.assume_role(role_arn, stage)


        # # Use the assumed_session to create the ACM certificate instance
        # acm_certificate_arn = "arn:aws:acm:us-east-1:633546161654:certificate/eb1794a2-4724-475a-9aad-b9e5bdaa38e3"
        # custom_domain_name = "d-kept97rbkf.execute-api.us-east-1.amazonaws.com"
        # acm_client = assumed_session.client('acm', region_name='us-east-1')
        # certificate = acm_client.get_certificate(CertificateArn=acm_certificate_arn)


        # # Create a DomainName resource
        # domain_name = apigateway_.DomainName(
        #     self, f"{stage.value}-CustomDomainName",
        #     domain_name=custom_domain_name,
        #     certificate=certificate,
        #     endpoint_type=apigateway_.EndpointType.REGIONAL,
        # )

        # # Create a BasePathMapping to associate the DomainName with your API stages
        # for custom_stage_name, stage_resources in self.resources.items():
        #     for resource_key, resource in stage_resources.items():
        #         base_path_mapping = apigateway_.BasePathMapping(
        #             self, f"{custom_stage_name}-{resource_key}-Mapping",
        #             domain_name=domain_name,
        #             rest_api=self.api,
        #             stage=resource.node.try_get_context('stage_name'),
        #             base_path=resource_key
        #         )
        
        # --------------------------------------------------------------------
        # TODO: Remove logic when custom domain is ready
        # Create a Lambda function for Store API URL after deployment
        api_url = self.api.url
        print_url_lambda = print_api_url_lambda(self, api_url, stage)
        rule = events_.Rule(self, f"{stage.name}-PrintApiUrlRule", schedule=events_.Schedule.expression('rate(365 days)'))
        rule.add_target(targets_.LambdaFunction(print_url_lambda, event=events_.RuleTargetInput.from_object({})))


    # Method to assume a role and return a new session
    def assume_role(self, role_arn: str, stage_name: StageName):
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')

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
            RoleSessionName=f"apigateway-{stage_name.value}-assumed-session"
        )

        # Extract the temporary credentials from the response
        credentials = response['Credentials']

        # Create a new session using the temporary credentials
        new_session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'],
        )

        return new_session
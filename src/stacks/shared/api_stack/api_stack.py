from aws_cdk import (
    Stack,
    aws_apigateway as apigateway_,
    aws_certificatemanager as acm_,
    CfnOutput,
)
from constructs import Construct
from src.utils.enums.stage_name import StageName
import boto3

class APIStack(Stack):
    @property
    def get_api(self):
        return self.api

    def __init__(self, scope: Construct, construct_id: str, stage_name: StageName, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Create a Rest API instance
        base_api = apigateway_.RestApi(
            self, "Integrations_Api", 
            rest_api_name="Integrations_Api", 
            description="Base API Gateway for Zato to AWS Migration",
            deploy_options=apigateway_.StageOptions(
                stage_name=stage_name.value, 
                logging_level=apigateway_.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
            endpoint_configuration=apigateway_.EndpointConfiguration(
                types=[apigateway_.EndpointType.REGIONAL]
            ),
        )

        # --------------------------------------------------------------------
        # TODO: Finsih task: create custom domain name for api gateway

        domain_name = "api.aws-integration-engine.com"
        acm = boto3.client('acm')
        response = acm.request_certificate(
            DomainName=domain_name,
            ValidationMethod='DNS'
        )

        # Get ARN of certificate
        certificate_arn = response['CertificateArn']

        domain_name_options = apigateway_.DomainNameOptions(
            certificate=acm.Certificate.from_certificate_arn(
                self, f"{stage_name.name}-AwsIntegrationEngine-CustomDomainCertificate",
                certificate_arn
            ),
            domain_name=domain_name
        )

        # Create the custom domain name
        domain_name = base_api.add_domain_name(
            f"{stage_name.name}-AwsIntegrationEngine-CustomDomainName",
            domain_name_options=domain_name_options,
        )

        # Add the domain name as an output
        CfnOutput(
            self, f"{stage_name.name}-AwsIntegrationEngine-CustomDomainNameOutput",
            value=domain_name.domain_name,
            description="Custom domain name for the Aws Integration Engine API",
        )


        self.api = base_api.root.add_resource("api")
    
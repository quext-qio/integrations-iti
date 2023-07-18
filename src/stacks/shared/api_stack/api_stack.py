from aws_cdk import (
    Stack,
    aws_apigateway as apigateway_,
    aws_certificatemanager as acm_,
)
from constructs import Construct
from src.utils.enums.stage_name import StageName

class APIStack(Stack):
    @property
    def get_api(self):
        return self.api

    def __init__(self, scope: Construct, construct_id: str, stage_name: StageName, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --------------------------------------------------------------------
        # Create a certificate from ACM
        domain_name = "api.aws-integration-engine.com"
        certificate = acm_.Certificate(
            self, f"{stage_name.name}-Integrations_Certificate",
            domain_name=domain_name,
            validation=acm_.CertificateValidation.from_dns(),
        )


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
            domain_name=apigateway_.DomainNameOptions(
                certificate=certificate,
                domain_name=domain_name,
            ),
        )
        self.api = base_api.root.add_resource("api")
    
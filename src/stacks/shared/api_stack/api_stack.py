from aws_cdk import (
    NestedStack,
    aws_apigateway as apigateway_,
    aws_certificatemanager as acm_,
)
from constructs import Construct
from src.utils.enums.stage_name import StageName

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
        # Create a certificate from ACM
        # domain_name = "api.aws-integration-engine.com"
        # certificate = acm_.Certificate(
        #     self, f"{stage_name.name}-Integrations_Certificate",
        #     domain_name=domain_name,
        #     validation=acm_.CertificateValidation.from_dns(),
        # )


        # --------------------------------------------------------------------
        # Create a Rest API instance
        base_api = apigateway_.RestApi(
            self, "Integrations_Api", 
            rest_api_name="Integrations_Api", 
            description="Base API Gateway for Zato to AWS Migration",
            deploy_options=apigateway_.StageOptions(
                stage_name=stage.value, 
                logging_level=apigateway_.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
            endpoint_configuration=apigateway_.EndpointConfiguration(
                types=[apigateway_.EndpointType.REGIONAL]
            ),
            # domain_name=apigateway_.DomainNameOptions(
            #     certificate=certificate,
            #     domain_name=domain_name,
            # ),
        )

        # Standard root resource
        api_resource = base_api.root.add_resource("api")
        self.api = api_resource

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

        # Create a dictionary of all the resources of v1
        dict_v1 = {
            "placepay": placepay_resource_v1,
            "resman": resman_resource_v1,
            "transunion": transunion_resource_v1,
            "general": general_resource_v1,
            "engrain": engrain_resource_v1,
            "tour": tour_resource_v1,
        }

        # Suported third party services v2
        placepay_resource_v2 = api_v2.add_resource("placepay")
        resman_resource_v2 = api_v2.add_resource("resman")
        transunion_resource_v2 = api_v2.add_resource("transunion")
        general_resource_v2 = api_v2.add_resource("general")
        engrain_resource_v2 = api_v2.add_resource("engrain")
        tour_resource_v2 = api_v2.add_resource("tour")

        # Create a dictionary of all the resources of v2
        dict_v2 = {
            "placepay": placepay_resource_v2,
            "resman": resman_resource_v2,
            "transunion": transunion_resource_v2,
            "general": general_resource_v2,
            "engrain": engrain_resource_v2,
            "tour": tour_resource_v2,
        }

        # Create a dictionary of all the resources and versions
        self.resources = {
            "v1": dict_v1,
            "v2": dict_v2,
        }

        # --------------------------------------------------------------------
        # stage_name = stage.value.lower()
        # custom_domain_name = f"{stage_name}-api-integration-engine"
        # domain_name = f"{custom_domain_name}.{self.region}.amazonaws.com"

        # # Create a certificate from ACM
        # certificate = acm_.Certificate(
        #     self, f"{stage.name}-Integrations_Certificate",
        #     domain_name=domain_name,
        #     validation=acm_.CertificateValidation.from_dns(),
        # )

        # base_api.add_domain_name(
        #     f"{stage_name}-MyCustomDomainName",
        #     domain_name=domain_name,
        #     certificate=certificate,
        #     endpoint_type=apigateway_.EndpointType.REGIONAL,
        # )


        # --------------------------------------------------------------------
        # Create a custom domain name for the API
        # Use the default ACM certificate for the domain name
        # certificate = acm_.Certificate.from_certificate_arn(
        #     self, "DefaultCertificate", 
        #     certificate_arn=f"arn:aws:acm:{self.region}:{self.account}:certificate/default"
        # )

        # Create the subdomain mapping for the API
        # subdomain = f"integrations-api-custom-{stage.value.lower()}"
        # domain = "execute-api"
        # suffix = f"{self.region}.amazonaws.com"
        # domain_name = f"{subdomain}.{domain}.{suffix}"
        # apigateway_.DomainName(
        #     self,
        #     f"{stage.value}-IntegrationsDomainName",
        #     domain_name=domain_name,
        #     certificate=default_certificate,
        #     mapping=base_api
        # )

        # base_api.add_domain_name(
        #     f"{stage_name.value.lower()}-MyCustomDomainName",
        #     domain_name=custom_domain.domain_name,
        #     certificate_name=custom_domain.certificate.certificate_name
        # )
    

    
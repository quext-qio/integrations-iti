from aws_cdk import (
    NestedStack,
    aws_apigateway as apigateway_,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_certificatemanager as acm_,
)
from constructs import Construct
from src.utils.enums.stage_name import StageName

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
                types=[apigateway_.EndpointType.REGIONAL]
            ),
        )

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

        # --------------------------------------------------------------------
        # TODO: Remove logic when custom domain is ready
        # Create a Lambda function for Store API URL after deployment
        api_url = self.api.url
        print_url_lambda = print_api_url_lambda(self, api_url, stage)
        rule = events_.Rule(self, f"{stage.name}-PrintApiUrlRule", schedule=events_.Schedule.expression('rate(365 days)'))
        rule.add_target(targets_.LambdaFunction(print_url_lambda, event=events_.RuleTargetInput.from_object({})))
   
       

        # # --------------------------------------------------------------------
        # # Test 1: Create a custom domain name for the API
        # stage_name = stage.value.lower()
        # custom_domain_name = f"{stage_name}-api-integration-engine"
        # domain_name = f"{custom_domain_name}.{self.region}.amazonaws.com"

        # # Create a certificate from ACM
        # certificate = acm_.Certificate(
        #     self, f"{stage.name}-Integrations_Certificate",
        #     domain_name=domain_name,
        #     validation=acm_.CertificateValidation.from_dns(),
        # )

        # self.api.add_domain_name(
        #     f"{stage_name}-MyCustomDomainName",
        #     domain_name=domain_name,
        #     certificate=certificate,
        #     endpoint_type=apigateway_.EndpointType.REGIONAL,
        # )    
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment
from aws_cdk import (
    NestedStack,
    aws_apigateway as apigateway_,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
)

# Lambda function to store the API URL after deployment
def print_api_url_lambda(scope: Construct, api_url: str, app_environment: AppEnvironment):
    return lambda_.Function(
        scope,
        f"{app_environment.get_stage_name()}-api-url-function",
        runtime=lambda_.Runtime.PYTHON_3_8,
        handler="index.handler",
        code=lambda_.Code.from_inline(
            "import os\n"
            "def handler(event, context):\n"
            f"    print('API URL for Aws Integration Engine in stage ({app_environment.name}):', '{api_url}')"
        ),
    )


class APIStack(NestedStack):
    @property
    def get_api(self):
        return self.api
    
    @property
    def get_resources(self):
        return self.resources


    def __init__(self, scope: Construct, construct_id: str, app_environment: AppEnvironment, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --------------------------------------------------------------------
        # Create a Rest API instance
        self.api = apigateway_.RestApi(
            self, f"{app_environment.get_stage_name()}-integrations-api", 
            rest_api_name=f"{app_environment.get_stage_name()}-integrations-api", 
            description=f"[{app_environment.get_stage_name().upper()}] Base API Gateway for Zato to AWS Migration",
            deploy=True,
            deploy_options=apigateway_.StageOptions(
                stage_name=app_environment.get_stage_name(), 
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
        # Set Custom Domain depending on the stage
        domain_config = app_environment.get_api_domain_config()
        hosted_zone_id = domain_config["hosted_zone_id"]
        domain_name_alias_target = domain_config["domain_name_alias_target"]
        custom_domain_name = domain_config["custom_domain_name"]
        
        # Get the domain name from the attributes
        api_domain = apigateway_.DomainName.from_domain_name_attributes(
            self, f"{app_environment.get_stage_name()}-domain-name",
            domain_name=custom_domain_name,
            domain_name_alias_hosted_zone_id=hosted_zone_id,
            domain_name_alias_target=domain_name_alias_target,
        )

        try:
            # Attempt to create the base mapping
            apigateway_.BasePathMapping(
                self, f"{app_environment.get_stage_name()}-base-path-mapping",
                domain_name=api_domain,
                rest_api=self.api,
                stage=self.api.deployment_stage,
            )
        except apigateway_.CfnBasePathMappingAlreadyExistsException:
            # If the base mapping already exists, catch the exception
            # and proceed without creating a new one.
            print("Base path mapping already exists.")
            pass     
        
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
        jira_resource_v1 = api_v1.add_resource("jira")

        # Create a dictionary of all the resources of v1
        dict_v1 = {
            "placepay": placepay_resource_v1,
            "resman": resman_resource_v1,
            "transunion": transunion_resource_v1,
            "general": general_resource_v1,
            "engrain": engrain_resource_v1,
            "tour": tour_resource_v1,
            "salesforce": salesforce_resource_v1,
            "jira": jira_resource_v1,
        }

        # Suported third party services v2
        placepay_resource_v2 = api_v2.add_resource("placepay")
        resman_resource_v2 = api_v2.add_resource("resman")
        transunion_resource_v2 = api_v2.add_resource("transunion")
        general_resource_v2 = api_v2.add_resource("general")
        engrain_resource_v2 = api_v2.add_resource("engrain")
        tour_resource_v2 = api_v2.add_resource("tour")
        salesforce_resource_v2 = api_v2.add_resource("salesforce")
        jira_resource_v2 = api_v2.add_resource("jira")
        one_time_link_v2 = api_v2.add_resource("security")

        # Create a dictionary of all the resources of v2
        dict_v2 = {
            "placepay": placepay_resource_v2,
            "resman": resman_resource_v2,
            "transunion": transunion_resource_v2,
            "general": general_resource_v2,
            "engrain": engrain_resource_v2,
            "tour": tour_resource_v2,
            "salesforce": salesforce_resource_v2,
            "jira": jira_resource_v2,
            "security": one_time_link_v2
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
        print_url_lambda = print_api_url_lambda(self, api_url, app_environment)
        rule = events_.Rule(self, f"{app_environment.name}-print-api-url-rule", schedule=events_.Schedule.expression('rate(365 days)'))
        rule.add_target(targets_.LambdaFunction(print_url_lambda, event=events_.RuleTargetInput.from_object({})))

from aws_cdk import (
    Stack,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class APIStack(Stack):
    @property
    def get_api(self):
        return self.api

    def __init__(self, scope: Construct, construct_id: str, stage_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --------------------------------------------------------------------
        # Create a Rest API instance
        base_api = apigateway_.RestApi(
            self, "Integrations_Api", 
            rest_api_name="Integrations_Api", 
            description="Base API Gateway for Zato to AWS Migration",
            deploy_options=apigateway_.StageOptions(
                stage_name=stage_name, 
                logging_level=apigateway_.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
            endpoint_configuration=apigateway_.EndpointConfiguration(
                types=[apigateway_.EndpointType.REGIONAL]
            ),
        )
        self.api = base_api.root.add_resource("api")
    
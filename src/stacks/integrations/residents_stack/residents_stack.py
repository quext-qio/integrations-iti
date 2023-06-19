from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class ResidentsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        environment={
            "LOG_LEVEL": "INFO",
            "AUTH_HOST": "https://auth-api.dev.quext.io",
            "IPS_HOST" : "https://partner-api.dev.quext.io"
        }
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']
        
        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /general/residents)
        lambda_function = lambda_.Function(
            self, 
            "Auth_Get_Residents",
            description="This Lambda is responsible to get a residents list according from AuthService", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/residents"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name="Auth_Get_Residents",
        )

        # -------------------------------------------------------------------- 
        # Add a resource to the base API and configure CORS options for the resource 
        # api = /api/v1/general/residents
        api = api.add_resource("residents",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # POST
        post_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ],
        )
        # --------------------------------------------------------------------
        # Add a POST method to endpoint
        api.add_method(
            'POST', 
            post_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ],
        )

from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct

class GuestcardsStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, environment: dict[str, str], **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Guestcards
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /general/guestcards)
        lambda_function = lambda_.Function(
            self, 
            "Guestcards_Lambda_Function",
            description="Guestcards Lambda is responsible save prospects information", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/guestcards"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name="Guestcards_Lambda_Function",
        )

        # --------------------------------------------------------------------
        # Add base resource to API Gateway
        # Resource to save prospects (POST)
        post_endpoint = api.add_resource(
            "guestcards",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),    
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # POST
        endpoint_lambda_integration = apigateway_.LambdaIntegration(
            lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                ),
            ],
        )


        # --------------------------------------------------------------------
        # Add a POST method to endpoint
        post_endpoint.add_method(
            'POST', 
            endpoint_lambda_integration,
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

        
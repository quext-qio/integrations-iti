from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment

class RentDynamicsStack(NestedStack):

    def __init__(self, scope: Construct, construct_id: str, api: apigateway_.RestApi, layers:list, environment: dict[str, str], app_environment: AppEnvironment, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Guestcards
        timeout=Duration.seconds(900)
        allow_methods=['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /general/rent-dynamics)
        lambda_function = lambda_.Function(
            self, 
            f"{app_environment.get_stage_name()}-rent-dynamics-lambda-function",
            description="This Lambda is responsible of rent-dynamics endpoints", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v2/rent_dynamics"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-rent-dynamics-lambda-function",
        )

        # --------------------------------------------------------------------
        # Add base resource to API Gateway
        # Resource to call rentdynamics endpoints (POST)
        post_endpoint = api.add_resource("{customerUUID}").add_resource("{action}").add_resource(
            "{communityUUID}",
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
            request_parameters={
                'method.request.path.customerUUID': True,
                'method.request.path.action': True,
                'method.request.path.communityUUID': False,
            },
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ],
        )

        
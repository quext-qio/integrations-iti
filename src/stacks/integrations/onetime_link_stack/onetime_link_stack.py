from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class OneTimeLinkStack(NestedStack):
    def __init__(
        self, scope: Construct, 
        construct_id: str, 
        api: apigateway_.RestApi, 
        layers: list, 
        environment: dict[str, str], 
        app_environment: AppEnvironment, 
        vpc,
        vpc_subnets,
        security_groups,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Guestcards
        timeout = Duration.seconds(900)
        allow_methods = ['OPTIONS', 'GET']

        # --------------------------------------------------------------------
        # Create lambda function instance for (#GET /security/onetimelink)
        lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-onetime-link-lambda-function",
            description="Endppoint to connect with One time link outgoing",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/onetime_link"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-onetime-link-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # --------------------------------------------------------------------
        # Add base resource to API Gateway
        get_endpoint = api.add_resource(
            "onetime_link",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # GET
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
        get_endpoint.add_method(
            'GET',
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

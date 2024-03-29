from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class PlacepayStack(NestedStack):
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
        # Constants
        timeout = Duration.seconds(900)
        allow_methods = ['OPTIONS', 'POST', 'GET']

        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /placepay/new-account)
        post_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-placepay-new-account-lambda-function",
            description="Placepay Lambda is responsible create new accounts using placepay package",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v1/placepay"),
            handler="post_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-placepay-new-account-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Create lambda function instance for (# GET /placepay/token?accountId=)
        get_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-placepay-token-lambda-function",
            description="Placepay Lambda is responsible create new access token placepay package",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v1/placepay"),
            handler="get_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-placepay-token-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # --------------------------------------------------------------------
        # Resource to create new account (POST)
        post_endpoint = api.add_resource(
            "new-account",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # Resource to create new access token (GET)
        get_endpoint = api.add_resource(
            "token",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
        # POST
        post_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            post_lambda_function,
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

        # GET
        get_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            get_lambda_function,
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

        # Add a GET method to endpoint
        get_endpoint.add_method(
            'GET',
            get_endpoint_lambda_integration,
            request_parameters={
                'method.request.querystring.accountId': True,
            },
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                ),
            ]
        )

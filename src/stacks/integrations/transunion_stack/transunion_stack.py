from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_

)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class TransUnionStack(NestedStack):
    def __init__(
        self, scope: Construct,
        construct_id: str,
        api: apigateway_.RestApi,
        layers: list,
        environment: dict,
        app_environment: AppEnvironment,
        vpc,
        vpc_subnets,
        security_groups,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        timeout = Duration.seconds(900)
        allow_methods = ["OPTIONS", "POST"]

        # ------------- handles the identity lambda ------------- #
        # Creates lambda function instance for (# POST /transunion/identity)
        identity_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-transunion-identity-lambda-function",
            description="Handles the verification and evaluation processes with TransUnion",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="identity_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-transunion-identity-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Identity
        identity_endpoint = api.add_resource(
            "identity",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # Create a Lambda integration instance
        # Identity
        identity_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            identity_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        identity_endpoint.add_method(
            "POST",
            identity_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                )
            ],
        )

        # ------------- handles the resident screening lambda ------------- #
        # Creates lambda function instance for (# POST /transunion/screening)
        screening_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-transunion-screening-lambda-function",
            description="Handles the resident screening processes with TransUnion",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="screening_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-transunion-screening-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Resident screening
        screening_endpoint = api.add_resource(
            "screening",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # Create a Lambda integration instance
        screening_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            screening_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        screening_endpoint.add_method(
            "POST",
            screening_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                )
            ],
        )

        # ------------- handles the postback lambda ------------- #
        # Creates lambda function instance for (# POST /transunion/postback)
        postback_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-transunion-postback-lambda-function",
            description="Handles the Postback webhook for TransUnion",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/transunion"),
            handler="postback_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-transunion-postback-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Postback webhook
        postback_endpoint = api.add_resource(
            "postback",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # Create a Lambda integration instance
        postback_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            postback_lambda_function,
            proxy=True,
            integration_responses=[
                apigateway_.IntegrationResponse(
                    status_code="200",
                    response_templates={"application/json": ""},
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    }
                ),
            ],
        )

        # Add a POST method to endpoint
        postback_endpoint.add_method(
            "POST",
            postback_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": True
                    }
                )
            ],
        )

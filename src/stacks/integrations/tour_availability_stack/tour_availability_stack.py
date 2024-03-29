from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class TourAvailabilityStack(NestedStack):
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

        timeout = Duration.seconds(900)
        allow_methods = ['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create lambda function instance
        lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-tour-availability-lambda-function",
            description="TourAvailability Lambda is responsible for times slots per community",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v2/tour_availability"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-tour-availability-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # --------------------------------------------------------------------
        # Add a resource to the base API and configure CORS options for the resource
        tour_availability_endpoint = api.add_resource(
            "tour-availability",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
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
                )
            ],
        )

        # --------------------------------------------------------------------
        # Add a POST method to endpoint
        tour_availability_endpoint.add_method(
            'POST',
            endpoint_lambda_integration,
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ],
        )

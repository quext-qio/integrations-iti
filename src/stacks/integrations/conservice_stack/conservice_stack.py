from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_ec2 as ec2_,
    aws_apigateway as apigateway_,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class ConserviceStack(NestedStack):

    def __init__(
            self, scope: Construct, 
            construct_id: str, 
            api: apigateway_.RestApi, 
            layers: list, 
            environment: dict, 
            app_environment: AppEnvironment, 
            vpc:  ec2_.Vpc,
            subnet_selection: ec2_.SubnetSelection,
            security_groups: list[ec2_.SecurityGroup],
            **kwargs
        ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # -----------------------------------------------------------------------
        # Constants
        timeout = Duration.seconds(900)
        allow_methods = ['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        # Create lambda function instance for (# POST /conservice)
        lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-conservice-lambda-function",
            description="Handles the Conservice endpoint requests",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v2/conservice"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-conservice-lambda-function",
            vpc=vpc,
            vpc_subnets=subnet_selection,
            security_groups=security_groups,
        )

        # --------------------------------------------------------------------
        # Add a resource to the base API and configure CORS options for the resource
        api = api.add_resource("conservice",
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

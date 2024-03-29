from aws_cdk import (
    NestedStack,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_apigateway as apigateway_,
    Duration,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class EngrainStack(NestedStack):
    def __init__(
        self, scope: Construct,
        construct_id: str,
        environment: dict[str, str],
        api: apigateway_.RestApi,
        layers: list,
        app_environment: AppEnvironment,
        vpc,
        vpc_subnets,
        security_groups,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Set maximun timeout for lambda functions
        # -----------------------------------------------------------------------
        # Constants
        allow_methods = ['OPTIONS', 'PATCH', 'GET']
        timeout = Duration.minutes(15)

        # --------------------------------------------------------------------
        # Create a Lambda function for Job Purposes
        lambda_fn = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-engrain-job-lambda-function",
            description="Engrain Job Lambda Function",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("./src/lambdas/v1/engrain"),
            handler="job_lambda_function.lambda_handler",
            function_name=f"{app_environment.get_stage_name()}-engrain-job-lambda-function",
            layers=layers,
            timeout=timeout,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Create a CloudWatch Event Rule
        event_rule = events_.Rule(
            self,
            f"{app_environment.get_stage_name()}-five-minutes-scheduled-event-rule",
            schedule=events_.Schedule.cron(minute="*/5"),
            description="CloudWatch Event Rule for execute Engrain Job every 5 minutes",
        )

        # Add the Lambda function as a target to the event rule
        event_rule.add_target(
            targets_.LambdaFunction(
                lambda_fn,
            ),
        )

        # --------------------------------------------------------------------
        # Create a Lambdas functions for [API] purposes

        # Create lambda function instance for (# GET /engrain/status)
        get_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-engrain-status-lambda-function",
            description="This endpoint is responsible for providing information on the execution permissions of the job, the date and time of the last execution, and if it is currently running.",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v1/engrain"),
            handler="get_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-engrain-status-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # Create lambda function instance for (# PATCH /engrain/status)
        patch_lambda_function = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-engrain-update-status-lambda-function",
            description="This endpoint is responsible to update the execution permissions of the job.",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v1/engrain"),
            handler="patch_lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-engrain-update-status-lambda-function",
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
            allow_public_subnet=True,
        )

        # --------------------------------------------------------------------
        # Add base resource to API Gateway

        # Resource to get status of the job (GET)
        get_endpoint = api.add_resource(
            "status",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # Resource to create update the status of the job (PATCH)
        patch_endpoint = api.add_resource(
            "job",
            default_cors_preflight_options=apigateway_.CorsOptions(
                allow_methods=allow_methods,
                allow_origins=apigateway_.Cors.ALL_ORIGINS
            ),
        )

        # --------------------------------------------------------------------
        # Create a Lambda integration instance
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

        # PATCH
        patch_endpoint_lambda_integration = apigateway_.LambdaIntegration(
            patch_lambda_function,
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
        # Add a GET method to endpoint
        get_endpoint.add_method(
            'GET',
            get_endpoint_lambda_integration,
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
        patch_endpoint.add_method(
            'PATCH',
            patch_endpoint_lambda_integration,
            request_parameters={},
            method_responses=[
                apigateway_.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                ),
            ]
        )

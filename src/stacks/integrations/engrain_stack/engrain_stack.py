from aws_cdk import (
    NestedStack,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_apigateway as apigateway_,
    Duration,
)
from constructs import Construct
import boto3

class EngrainStack(NestedStack):
    def __init__(self, scope: Construct, construct_id: str, environment: dict[str, str], api: apigateway_.RestApi, layers:list, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Set maximun timeout for lambda functions
        # -----------------------------------------------------------------------
        # Constants
        allow_methods=['OPTIONS', 'PATCH', 'GET']
        timeout=Duration.minutes(15)
        
        # --------------------------------------------------------------------
        # Create a Lambda function for Job Purposes
        lambda_fn = lambda_.Function(
            self,
            "Engrain_Job_Function",
            description="Engrain Job Lambda Function", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("./src/lambdas/engrain"),
            handler="job_lambda_function.lambda_handler",
            function_name="Engrain_Job_Function",
            layers=layers,
            timeout=timeout,
        )

        # Create a CloudWatch Event Rule
        event_rule = events_.Rule(
            self,
            f"FiveMinutesScheduledEvent",
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
            "Engrain_Status_Lambda_Function",
            description="This endpoint is responsible for providing information on the execution permissions of the job, the date and time of the last execution, and if it is currently running.",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/engrain"),
            handler="get_lambda_function.lambda_handler",
            layers=layers,
            function_name="Engrain_Status_Lambda_Function",
        )
        
        # Create lambda function instance for (# PATCH /engrain/status)
        patch_lambda_function = lambda_.Function(
            self, 
            "Engrain_Update_Status_Lambda_Function",
            description="This endpoint is responsible to update the execution permissions of the job.",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/engrain"),
            handler="patch_lambda_function.lambda_handler",
            layers=layers,
            function_name="Engrain_Update_Status_Lambda_Function",
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


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

class TruePayGoogleStack(NestedStack):
    def __init__(
        self, scope: Construct, 
        construct_id: str, 
        environment: dict[str, str], 
        layers:list, 
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
        timeout=Duration.minutes(15)
        
        # --------------------------------------------------------------------
        # Create a Lambda function for Job Purposes
        lambda_fn = lambda_.Function(
            self,
            f"{app_environment.get_stage_name()}-trupay-google-job-lambda-function",
            description="TruPay Google Lambda Function", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("./src/lambdas/v1/trupay_google"),
            handler="job_lambda_function.lambda_handler",
            function_name=f"{app_environment.get_stage_name()}-trupay-google-job-lambda-function",
            layers=layers,
            timeout=timeout,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            security_groups=security_groups,
        )

        # Create a CloudWatch Event Rule
        event_rule = events_.Rule(
            self,
            f"{app_environment.get_stage_name()}-trupay-google-five-minutes-scheduled-event-rule",
            schedule=events_.Schedule.cron(minute="*/5"),
            description="CloudWatch Event Rule for execute (TruPay Google) every 5 minutes",
        )

        # Add the Lambda function as a target to the event rule
        event_rule.add_target(
            targets_.LambdaFunction(
                lambda_fn,
            ),
        )
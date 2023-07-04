from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
)
from constructs import Construct

class EngrainStack(Stack):
    
    def __init__(self, scope: Construct, construct_id: str, environment: dict[str, str],  layers:list, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # --------------------------------------------------------------------
        # Create a Lambda function
        lambda_fn = lambda_.Function(
            self,
            "Engrain_Job_Function",
            description="Engrain Job Lambda Function", 
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            code=lambda_.Code.from_asset("./src/lambdas/engrain"),
            handler="lambda_function.lambda_handler",
            function_name="Engrain_Job_Function",
            layers=layers,
        )

        # Create a CloudWatch Event Rule
        event_rule = events_.Rule(
            self,
            "FiveMinutesScheduledEvent",
            schedule=events_.Schedule.rate(Duration.minutes(5)),
        )
        
        # Add the Lambda function as a target to the event rule
        event_rule.add_target(targets_.LambdaFunction(lambda_fn))

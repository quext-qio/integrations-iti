import boto3
from aws_cdk import (
    NestedStack,
    Duration,
    aws_lambda as lambda_,
    aws_apigateway as apigateway_,
    aws_sqs as sqs_,
    aws_iam as iam_,
    aws_lambda_event_sources as lambda_event_sources_,
    Aws,
)
from constructs import Construct
from src.utils.enums.app_environment import AppEnvironment


class QoopsStack(NestedStack):
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
        # allow_methods=['OPTIONS', 'POST']

        # --------------------------------------------------------------------
        try:
            # Create the QoopsQueue
            queue = sqs_.Queue(
                self,
                f"{app_environment.get_stage_name()}-queue",
                visibility_timeout=timeout,
                queue_name=f"{app_environment.get_stage_name()}-queue",
            )
        except Exception as e:
            print(f"Error creating queue: {e}")

        # --------------------------------------------------------------------
        # Create the API GW service role with permissions to call SQS
        try:
            rest_api_role = iam_.Role(
                self,
                f"{app_environment.get_stage_name()}-role",
                role_name=f"{app_environment.get_stage_name()}-role",
                description="Qoops Role for API Gateway to call SQS",
                assumed_by=iam_.ServicePrincipal("apigateway.amazonaws.com"),
            )

            # Attach a policy granting permissions to send messages to the SQS queue
            sqs_policy = iam_.Policy(
                self,
                f"{app_environment.get_stage_name()}-sqs-policy",
                statements=[
                    iam_.PolicyStatement(
                        actions=["sqs:SendMessage"],
                        resources=[queue.queue_arn],
                    )
                ],
            )
            rest_api_role.attach_inline_policy(sqs_policy)

        except Exception as e:
            print(f"Error creating role for SQS: {e}")
            raise PermissionError(f"Error creating role for SQS: {e}")

        # --------------------------------------------------------------------
        # Create API Integration Response object:
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationResponse.html
        integration_response = apigateway_.IntegrationResponse(
            status_code="200",
            response_templates={"application/json": ""},
        )

        # --------------------------------------------------------------------
        # Create API Integration Options object:
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/IntegrationOptions.html
        try:
            api_integration_options = apigateway_.IntegrationOptions(
                credentials_role=rest_api_role,
                integration_responses=[integration_response],
                request_templates={
                    "application/json": "Action=SendMessage&MessageBody=$input.body"},
                passthrough_behavior=apigateway_.PassthroughBehavior.NEVER,
                request_parameters={
                    "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"},
            )
        except Exception as e:
            print(f"Error creating API Integration Options: {e}")
            raise PermissionError(
                f"Error creating API Integration Options: {e}")

        # --------------------------------------------------------------------
        # Create AWS Integration Object for SQS:
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/AwsIntegration.html
        api_resource_sqs_integration = apigateway_.AwsIntegration(
            service="sqs",
            integration_http_method="POST",
            options=api_integration_options,
            path="{}/{}".format(Aws.ACCOUNT_ID, queue.queue_name),
        )

        # --------------------------------------------------------------------
        # Create a Method Response Object:
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_apigateway/MethodResponse.html
        method_response = apigateway_.MethodResponse(status_code="200")

        # --------------------------------------------------------------------
        # Add the API GW Integration to the API GW Resource
        api.add_resource("qoops").add_method(
            "POST",
            api_resource_sqs_integration,
            method_responses=[method_response]
        )

        # --------------------------------------------------------------------
        # Creating Lambda function that will be triggered by the SQS Queue
        sqs_lambda = lambda_.Function(
            self, f"{app_environment.get_stage_name()}-qoops-lambda",
            description=f"This lambda is used to report Jira issues using the qoops-queue",
            environment=environment,
            runtime=lambda_.Runtime.PYTHON_3_10,
            timeout=timeout,
            code=lambda_.Code.from_asset("./src/lambdas/v2/qoops"),
            handler="lambda_function.lambda_handler",
            layers=layers,
            function_name=f"{app_environment.get_stage_name()}-qoops-lambda",
        )

        # --------------------------------------------------------------------
        # Check if the event source mapping already exists
        mapping_exists = False
        try:
            client = boto3.client('lambda')
            response = client.list_event_source_mappings(
                EventSourceArn=queue.queue_arn,
                FunctionName=sqs_lambda.function_name
            )
            if 'EventSourceMappings' in response:
                mapping_exists = True

        except Exception as e:
            print(f"Error checking event source mapping: {e}")

        # If the event source mapping does not exist, create it
        if not mapping_exists:
            try:
                # Create an SQS event source for Lambda
                sqs_event_source = lambda_event_sources_.SqsEventSource(queue)
            except Exception as e:
                print(f"Error creating SQS event source: {e}")
                raise PermissionError(f"Error creating SQS event source: {e}")

            try:
                # Add SQS event source to the Lambda function
                sqs_lambda.add_event_source(sqs_event_source)
            except Exception as e:
                print(f"Error adding SQS event source: {e}")
                raise PermissionError(f"Error adding SQS event source: {e}")
        else:
            print("Event source mapping already exists.")
